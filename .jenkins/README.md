# Jenkins pipeline

This folder contains helper code used by `Jenkinsfile`.

Expected Jenkins credentials:

| ID | Type | Purpose |
| --- | --- | --- |
| `aws-jenkins-ecr` | Username with password | AWS access key ID as username, AWS secret access key as password |
| `aws-jenkins-session-token` | Secret text | Optional STS session token when `USE_AWS_SESSION_TOKEN=true` |
| `github-repo-token` | Username with password | GitHub token used for app checkout and GitOps updates |

Jenkins updates GitOps through HTTPS with a token, then Argo CD deploys from Git.
