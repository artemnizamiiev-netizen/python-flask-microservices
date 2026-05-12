# Jenkins pipeline

This folder contains helper code used by `Jenkinsfile`.

Expected Jenkins credentials:

| ID | Type | Purpose |
| --- | --- | --- |
| `aws-jenkins-ecr` | Username with password | AWS access key ID as username, AWS secret access key as password |
| `aws-jenkins-session-token` | Secret text | Optional STS session token when `USE_AWS_SESSION_TOKEN=true` |
| `github-gitops-token` | Secret text | GitHub token with write access to the GitOps repo |

Jenkins updates GitOps through HTTPS with a token, then Argo CD deploys from Git.
