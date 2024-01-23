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

        stage ('Deploy') {
            steps {
                script {
                        azureCLI commands: [[
                            exportVariablesString: 'containerInstanceName, registry_name, image_repository',
                            script: '''
                                az container create --resource-group owwll-recommendation-fastapi-ci-cd_dev \
                                    --name ${containerInstanceName} \
                                    --image ${registry_name}/${image_repository}:${env.BUILD_TAG} \
                                    --cpu 1 --memory 1 \
                                    --registry-login-server ${registry_name} \
                                    --registry-username owwllFastApiCR \
                                    --registry-password L9hhyrtOBwgoB8J0Jw62h8aWTZUsCWvelpAPeY1Oi++ACRB7JmIC \
                                    --ip-address Public \
                                    --dns-name-label owwll-ap-instance \
                                    --ports 80
                            '''
                        ]]
                } 
                    
            }
        }
    }
}

