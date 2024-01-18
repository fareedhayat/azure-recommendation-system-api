pipeline {
	agent any 

    environment {
        dockerHome = tool 'myDocker'
        PATH = "$dockerHome/bin:$PATH"
        registry_credentials = 'ACR_FASTAPI'
        registry_URL = 'https://owwllfastapicr.azurecr.io'
        registry_name = 'owwllfastapicr'
        image_name = 'recommendation-sytem-api'
        docker_image = ''
    }

	stages {
		stage ('Build') {
			steps {
				echo "Building Docker Image"
                script {
                    docker_image = docker.build("${registry_name}/${image_name}:${env.BUILD_TAG}")
                }
		    }
        }

		stage ('Upload') {
			steps {	
                script {
                    withCredentials([azureServicePrincipal('34a5f951-6d0f-4665-ae04-6cc649cdefd9')]) {
                        sh 'az --version'
                    }
                    withDockerRegistry(credentialsId:"${registry_credentials}" , url: "${registry_URL}") {
                        docker_image.push()
                    }
                }
			}
		}
}
}
