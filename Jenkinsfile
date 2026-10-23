pipeline {
    agent any

    environment {
        PATH = "C:\\Users\\Bruger\\AppData\\Local\\Programs\\Python\\Python311;C:\\Users\\Bruger\\AppData\\Local\\Programs\\Python\\Python311\\Scripts;${env.PATH}"
    }

    stages {
        stage('Validate Environment') {
            steps {
                bat 'python --version'
                bat 'python -m pip --version'
            }
        }

        stage('Create Test Environment') {
            steps {
                bat '''
                    if exist .jenkins-venv rmdir /s /q .jenkins-venv
                    python -m venv .jenkins-venv
                    .jenkins-venv\\Scripts\\python.exe -m pip install --upgrade pip setuptools
                    .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements.txt
                    .jenkins-venv\\Scripts\\python.exe -m pip install -e helper-package
                '''
            }
        }

        stage('Validate Build') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m compileall api-service
                    .jenkins-venv\\Scripts\\python.exe -m compileall resource-service
                    .jenkins-venv\\Scripts\\python.exe -m compileall processing-service
                    .jenkins-venv\\Scripts\\python.exe -m compileall helper-package
                '''
            }
        }

        stage('Unit and Authorization Tests') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m pytest tests/test_api.py tests/test_resource.py -v --junitxml=artifacts/unit-tests.xml
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m pytest tests/test_integration.py -v --junitxml=artifacts/integration-tests.xml
                '''
            }
        }

        stage('Static Security Analysis') {
            steps {
                script {
                    bat(
                        returnStatus: true,
                        script: '.jenkins-venv\\Scripts\\python.exe -m bandit -r api-service resource-service processing-service helper-package -f json -o artifacts\\bandit-report.json'
                    )
                }

                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m bandit -r api-service resource-service processing-service helper-package -ll
                '''
            }
        }

        stage('Dependency Security Analysis') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m pip_audit -f json -o artifacts\\pip-audit-report.json
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'artifacts/*-tests.xml', allowEmptyResults: true

            archiveArtifacts artifacts: 'artifacts/**/*',
                             allowEmptyArchive: true
        }
    }
}