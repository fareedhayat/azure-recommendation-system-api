pipeline {
	agent any 

    environment {
        dockerHome = tool 'myDocker'
        PATH = "$dockerHome/bin:$PATH"
        registry_credentials = 'fastapi_acr'
        registry_URL = 'https://owwllfastapicr.azurecr.io'
        image_repository = 'owwllfastapicr/recommendation-sytem-api'
        registry_name = 'owwllfastapicr'
        image_name = 'recommendation-sytem-api'
        containerInstanceName = 'jenkins-owwllfastapi-ci-cd'
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
                    docker.withRegistry( "${registry_URL}", registry_credentials ) {
                    docker_image.push()
                    }
                }
			}
		}
    }
}

