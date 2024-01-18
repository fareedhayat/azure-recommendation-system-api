pipeline {
	agent any 

    environment {
        dockerHome = tool 'myDocker'
        PATH = "$dockerHome/bin:$PATH"
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
				echo "Uploading Docker Image to Azure Container Registry"
			}
		}
	}
}