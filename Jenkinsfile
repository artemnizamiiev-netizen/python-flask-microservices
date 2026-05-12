def SERVICES = [
  [
    name: 'frontend',
    context: 'frontend',
    repository: 'frontend',
    requirements: 'frontend/requirements.txt',
    tests: 'frontend/tests'
  ],
  [
    name: 'user-service',
    context: 'user-service',
    repository: 'user-service',
    requirements: 'user-service/requirements.txt',
    tests: 'user-service/tests'
  ],
  [
    name: 'product-service',
    context: 'product-service',
    repository: 'product-service',
    requirements: 'product-service/requirements.txt',
    tests: 'product-service/tests'
  ],
  [
    name: 'order-service',
    context: 'order-service',
    repository: 'order-service',
    requirements: 'order-service/requirements.txt',
    tests: 'order-service/tests'
  ]
]

pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '20'))
    disableConcurrentBuilds()
    timestamps()
  }

  parameters {
    string(name: 'AWS_ACCOUNT_ID', defaultValue: '212351100079', description: 'AWS account ID that owns the ECR repositories.')
    choice(name: 'DEPLOY_ENV', choices: ['jenkins-kind'], description: 'GitOps environment that Jenkins updates after pushing images.')
    string(name: 'IMAGE_TAG', defaultValue: '', description: 'Optional image tag. Empty value becomes sha-<full git sha>.')
    booleanParam(name: 'USE_AWS_SESSION_TOKEN', defaultValue: false, description: 'Enable when AWS credentials include an AWS_SESSION_TOKEN.')
    booleanParam(name: 'PUSH_IMAGES', defaultValue: true, description: 'Push built Docker images to ECR.')
    booleanParam(name: 'UPDATE_GITOPS', defaultValue: true, description: 'Commit the new image repositories and tags to the GitOps repository.')
  }

  environment {
    AWS_REGION = 'eu-central-1'
    AWS_ECR_CREDENTIALS_ID = 'aws-jenkins-ecr'
    AWS_SESSION_TOKEN_CREDENTIALS_ID = 'aws-jenkins-session-token'
    GITOPS_REPO_URL = 'git@github.com:artemnizamiiev-netizen/python-flask-microservices-gitops.git'
    GITOPS_SSH_CREDENTIALS_ID = 'github-gitops-ssh'
    DOCKER_BUILDKIT = '1'
  }

  stages {
    stage('Prepare metadata') {
      steps {
        script {
          env.FULL_SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
          env.SHORT_SHA = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
          env.IMAGE_TAG_EFFECTIVE = params.IMAGE_TAG?.trim() ? params.IMAGE_TAG.trim() : "sha-${env.FULL_SHA}"
          env.ECR_REGISTRY = "${params.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"
          currentBuild.displayName = "#${env.BUILD_NUMBER} ${env.SHORT_SHA}"
        }
      }
    }

    stage('Unit tests') {
      steps {
        sh 'mkdir -p reports'
        script {
          def testStages = SERVICES.collectEntries { service ->
            ["pytest / ${service.name}": {
              sh(
                label: "pytest ${service.name}",
                script: """
                  docker run --rm \
                    -v "\$PWD:/workspace" \
                    -w /workspace \
                    python:3.7-buster \
                    bash -lc 'python -m pip install --upgrade pip setuptools wheel && \
                              python -m pip install -r ${service.requirements} && \
                              python -m pip install -r requirements-dev.txt && \
                              pytest -q ${service.tests} --junitxml=reports/${service.name}-junit.xml'
                """
              )
            }]
          }

          parallel testStages
        }
      }
    }

    stage('Login to ECR') {
      when {
        expression { return params.PUSH_IMAGES }
      }
      steps {
        script {
          def loginToEcr = {
            sh(
              label: 'aws ecr login',
              script: '''
                aws ecr get-login-password --region "$AWS_REGION" \
                  | docker login --username AWS --password-stdin "$ECR_REGISTRY"
              '''
            )
          }

          if (params.USE_AWS_SESSION_TOKEN) {
            withCredentials([
              usernamePassword(
                credentialsId: env.AWS_ECR_CREDENTIALS_ID,
                usernameVariable: 'AWS_ACCESS_KEY_ID',
                passwordVariable: 'AWS_SECRET_ACCESS_KEY'
              ),
              string(
                credentialsId: env.AWS_SESSION_TOKEN_CREDENTIALS_ID,
                variable: 'AWS_SESSION_TOKEN'
              )
            ]) {
              loginToEcr()
            }
          } else {
            withCredentials([
              usernamePassword(
                credentialsId: env.AWS_ECR_CREDENTIALS_ID,
                usernameVariable: 'AWS_ACCESS_KEY_ID',
                passwordVariable: 'AWS_SECRET_ACCESS_KEY'
              )
            ]) {
              loginToEcr()
            }
          }
        }
      }
    }

    stage('Build and push images') {
      when {
        expression { return params.PUSH_IMAGES }
      }
      steps {
        script {
          def imageStages = SERVICES.collectEntries { service ->
            ["image / ${service.name}": {
              def image = "${env.ECR_REGISTRY}/${service.repository}"
              sh(
                label: "docker build/push ${service.name}",
                script: """
                  docker build \
                    --label org.opencontainers.image.revision=${env.FULL_SHA} \
                    -t ${image}:${env.IMAGE_TAG_EFFECTIVE} \
                    -t ${image}:latest \
                    ${service.context}

                  docker push ${image}:${env.IMAGE_TAG_EFFECTIVE}
                  docker push ${image}:latest
                """
              )
            }]
          }

          parallel imageStages
        }
      }
    }

    stage('Update GitOps repo') {
      when {
        expression { return params.PUSH_IMAGES && params.UPDATE_GITOPS }
      }
      steps {
        sshagent(credentials: [env.GITOPS_SSH_CREDENTIALS_ID]) {
          dir('gitops') {
            deleteDir()
            sh '''
              GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" \
                git clone --branch main "$GITOPS_REPO_URL" .
            '''
          }

          sh(
            label: 'update GitOps image values',
            script: '''
              python3 .jenkins/scripts/update_gitops_tags.py \
                --gitops-dir gitops \
                --environment "$DEPLOY_ENV" \
                --registry "$ECR_REGISTRY" \
                --tag "$IMAGE_TAG_EFFECTIVE"
            '''
          )

          dir('gitops') {
            sh '''
              git config user.name "jenkins[bot]"
              git config user.email "jenkins[bot]@users.noreply.github.com"

              git add "environments/${DEPLOY_ENV}"/*/values.yaml

              if git diff --cached --quiet; then
                echo "No GitOps changes to commit."
              else
                git commit -m "chore(${DEPLOY_ENV}): deploy ${SHORT_SHA}"
                GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" git push origin HEAD:main
              fi
            '''
          }
        }
      }
    }
  }

  post {
    always {
      junit allowEmptyResults: true, testResults: 'reports/*-junit.xml'
      archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/*-junit.xml'
      cleanWs deleteDirs: true, disableDeferredWipeout: true, notFailBuild: true
    }
  }
}
