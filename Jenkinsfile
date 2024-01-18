pipeline {
	agent any 

    environment {
        dockerHome = tool 'myDocker'
        PATH = "$dockerHome/bin:$PATH"
        registry_credentials = 'ACR_FASTAPI'
        registry_URL = 'owwllfastapicr.azurecr.io'
    }

	stages {
		stage ('Build') {
			steps {
				echo "Building Docker Image"
                script {
                    docker_image = docker.build("fareedhayat/recommendation-sytem-api:${env.BUILD_TAG}")
                }
			}
		}
		stage ('Upload') {
			steps {
				withDockerRegistry(credentialsId:${registry_credentials} , toolName: 'myDocker', url: ${registry_URL}) {
                    docker_image.push()
            }
			}
		}
	}
}