def SERVICES = [
  [
    name: 'frontend',
    context: 'frontend',
    repository: 'frontend',
    requirements: 'frontend/requirements.txt',
    tests: 'frontend/tests',
    helmChart: 'charts/frontend'
  ],
  [
    name: 'user-service',
    context: 'user-service',
    repository: 'user-service',
    requirements: 'user-service/requirements.txt',
    tests: 'user-service/tests',
    helmChart: 'charts/common-service'
  ],
  [
    name: 'product-service',
    context: 'product-service',
    repository: 'product-service',
    requirements: 'product-service/requirements.txt',
    tests: 'product-service/tests',
    helmChart: 'charts/common-service'
  ],
  [
    name: 'order-service',
    context: 'order-service',
    repository: 'order-service',
    requirements: 'order-service/requirements.txt',
    tests: 'order-service/tests',
    helmChart: 'charts/common-service'
  ]
]

pipeline {
  agent { label 'ec2-fleet' }

  options {
    buildDiscarder(logRotator(numToKeepStr: '20'))
    disableConcurrentBuilds()
    timestamps()
  }

  parameters {
    string(name: 'AWS_ACCOUNT_ID', defaultValue: '212351100079', description: 'AWS account ID that owns the ECR repositories.')
    string(name: 'AWS_REGION', defaultValue: 'eu-central-1', description: 'AWS region for ECR and the future EKS deployment.')
    string(name: 'IMAGE_TAG', defaultValue: '', description: 'Optional image tag. Empty value becomes sha-<full git sha>.')

    booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run unit tests before building images.')
    booleanParam(name: 'PUSH_IMAGES', defaultValue: true, description: 'Build and push Docker images to ECR.')

    booleanParam(name: 'DEPLOY_TO_EKS', defaultValue: false, description: 'Deploy with Helm to an existing EKS cluster. Keep disabled until the cluster is ready.')
    string(name: 'EKS_CLUSTER_NAME', defaultValue: 'TODO-existing-eks-cluster-name', description: 'Existing EKS cluster name. Placeholder until EKS is created by Terragrunt.')
    string(name: 'K8S_NAMESPACE', defaultValue: 'microservices-dev', description: 'Kubernetes namespace for the deployment.')
    string(name: 'DEPLOY_ENVIRONMENT', defaultValue: 'dev', description: 'Values directory under environments/<name> in the Helm repo.')
    string(name: 'HELM_REPO_URL', defaultValue: 'https://github.com/artemnizamiiev-netizen/python-flask-microservices-gitops.git', description: 'Repository that contains Helm charts and environment values.')
    string(name: 'HELM_REPO_BRANCH', defaultValue: 'main', description: 'Branch with Helm charts and values.')
    string(name: 'HELM_REPO_CREDENTIALS_ID', defaultValue: 'github-repo-token', description: 'Optional Jenkins credential ID for cloning the Helm repo.')

    booleanParam(name: 'RUN_SMOKE_TEST', defaultValue: false, description: 'Run a smoke check after deploy.')
    string(name: 'SMOKE_TEST_URL', defaultValue: 'TODO-service-url/healthz', description: 'Placeholder URL for a post-deploy smoke check.')
  }

  environment {
    DOCKER_BUILDKIT = '0'
  }

  stages {
    stage('Prepare metadata') {
      steps {
        script {
          env.AWS_REGION_EFFECTIVE = params.AWS_REGION.trim()
          env.FULL_SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
          env.SHORT_SHA = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
          env.IMAGE_TAG_EFFECTIVE = params.IMAGE_TAG?.trim() ? params.IMAGE_TAG.trim() : "sha-${env.FULL_SHA}"
          env.ECR_REGISTRY = "${params.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION_EFFECTIVE}.amazonaws.com"
          currentBuild.displayName = "#${env.BUILD_NUMBER} ${env.SHORT_SHA}"
          currentBuild.description = "tag=${env.IMAGE_TAG_EFFECTIVE}"
        }
      }
    }

    stage('Verify agent') {
      steps {
        sh(
          label: 'agent tools and identity',
          script: '''
            set -eu
            hostname
            whoami
            docker --version
            git --version
            java -version
            aws --version
            python3 -c "import yaml; print('yaml ok')"
            aws sts get-caller-identity
            df -h / /tmp
          '''
        )
      }
    }

    stage('Unit tests') {
      when {
        expression { return params.RUN_TESTS }
      }
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
        sh(
          label: 'aws ecr login via agent role',
          script: '''
            aws ecr get-login-password --region "$AWS_REGION_EFFECTIVE" \
              | docker login --username AWS --password-stdin "$ECR_REGISTRY"
          '''
        )
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

    stage('Deploy to EKS') {
      when {
        expression { return params.DEPLOY_TO_EKS }
      }
      steps {
        script {
          if (!params.EKS_CLUSTER_NAME?.trim() || params.EKS_CLUSTER_NAME.startsWith('TODO')) {
            error('EKS_CLUSTER_NAME is still a placeholder. Create/select the existing EKS cluster first.')
          }

          sh(
            label: 'check deploy tools',
            script: '''
              command -v kubectl >/dev/null || { echo "kubectl is missing on the Jenkins agent. Add it to the agent bootstrap/AMI before enabling DEPLOY_TO_EKS."; exit 1; }
              command -v helm >/dev/null || { echo "helm is missing on the Jenkins agent. Add it to the agent bootstrap/AMI before enabling DEPLOY_TO_EKS."; exit 1; }
            '''
          )

          sh(
            label: 'configure kubeconfig',
            script: '''
              aws eks update-kubeconfig \
                --region "$AWS_REGION_EFFECTIVE" \
                --name "$EKS_CLUSTER_NAME"

              kubectl get nodes
            '''
          )

          dir('helm-repo') {
            deleteDir()
          }

          if (params.HELM_REPO_CREDENTIALS_ID?.trim()) {
            withCredentials([
              usernamePassword(
                credentialsId: params.HELM_REPO_CREDENTIALS_ID.trim(),
                usernameVariable: 'GIT_USERNAME',
                passwordVariable: 'GIT_PASSWORD'
              )
            ]) {
              sh(
                label: 'clone Helm repo with credentials',
                script: '''
                  cat > "$WORKSPACE/.git-askpass.sh" <<'EOF'
#!/bin/sh
case "$1" in
  *Username*) echo "$GIT_USERNAME" ;;
  *Password*) echo "$GIT_PASSWORD" ;;
  *) echo "" ;;
esac
EOF
                  chmod 700 "$WORKSPACE/.git-askpass.sh"
                  trap 'rm -f "$WORKSPACE/.git-askpass.sh"' EXIT

                  GIT_ASKPASS="$WORKSPACE/.git-askpass.sh" \
                    GIT_TERMINAL_PROMPT=0 \
                    git clone --branch "$HELM_REPO_BRANCH" "$HELM_REPO_URL" helm-repo
                '''
              )
            }
          } else {
            sh(
              label: 'clone Helm repo',
              script: 'git clone --branch "$HELM_REPO_BRANCH" "$HELM_REPO_URL" helm-repo'
            )
          }

          def deployStages = SERVICES.collectEntries { service ->
            ["helm / ${service.name}": {
              def image = "${env.ECR_REGISTRY}/${service.repository}"
              def valuesFile = "helm-repo/environments/${params.DEPLOY_ENVIRONMENT.trim()}/${service.name}/values.yaml"
              sh(
                label: "helm upgrade ${service.name}",
                script: """
                  test -f ${valuesFile}

                  helm upgrade --install ${service.name} helm-repo/${service.helmChart} \
                    --namespace "$K8S_NAMESPACE" \
                    --create-namespace \
                    -f ${valuesFile} \
                    --set image.repository=${image} \
                    --set image.tag=${env.IMAGE_TAG_EFFECTIVE} \
                    --wait \
                    --timeout 5m
                """
              )
            }]
          }

          parallel deployStages
        }
      }
    }

    stage('Smoke test') {
      when {
        expression { return params.DEPLOY_TO_EKS && params.RUN_SMOKE_TEST }
      }
      steps {
        script {
          if (!params.SMOKE_TEST_URL?.trim() || params.SMOKE_TEST_URL.startsWith('TODO')) {
            error('SMOKE_TEST_URL is still a placeholder.')
          }
        }

        sh(
          label: 'smoke check',
          script: '''
            curl -fsS "$SMOKE_TEST_URL"
          '''
        )
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
