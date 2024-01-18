pipeline {
	agent any 

    environment {
        dockerHome = tool 'myDocker'
        PATH = "$dockerHome/bin:$PATH"
        registry_credentials = 'ACR_FASTAPI'
        registry_URL = 'https://owwllfastapicr.azurecr.io'
        registry_name = 'owwllfastapicr'
        image_name = 'recommendation-sytem-api'
    }

	stages {
		stage ('Build') {
			steps {
                withCredentials([azureServicePrincipal('34a5f951-6d0f-4665-ae04-6cc649cdefd9')]) {
                    script {
                        // Set the PATH to include the Azure CLI directory
                        env.PATH = "/path/to/azure-cli:${env.PATH}"

                        // Now, az should be available in the PATH
                        sh 'az --version'
				echo "Building Docker Image"
                script {
                    docker_image = docker.build("${registry_name}/${image_name}:${env.BUILD_TAG}")
                }
			}
            }
		}
		stage ('Upload') {
			steps {
				withDockerRegistry(credentialsId:"${registry_credentials}" , url: "${registry_URL}") {
                    script {
                        sh "az acr login --name ${registry_name}"
                        docker_image.push()
                    }
            }
			}
		}
	}
}