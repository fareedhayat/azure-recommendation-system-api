pipeline {
	agent any 
	stages {
		stage ('Build') {
			steps {
				sh 'mvn --version'
				echo "build"
			}
		}
		stage ('Deployment') {
			steps {
				echo "Deployment"
			}
		}
	}
}