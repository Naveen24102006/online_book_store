
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        DOCKER_EXE = 'C:\\Users\\NAVEEN\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        KUBECTL_EXE = 'C:\\Users\\NAVEEN\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'
        DOCKER_IMAGE = 'naveen24102006/online-book-store:latest'
    }

    stages {
        stage('Clone Code') {
            steps {
                checkout scm
                bat 'dir'
            }
        }

        stage('Check Docker and kubectl') {
            steps {
                bat '''
                    "%DOCKER_EXE%" --version
                    "%DOCKER_EXE%" info
                    "%KUBECTL_EXE%" version --client
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER_EXE%" build -t "%DOCKER_IMAGE%" .'
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    try {
                        bat '''
                            "%DOCKER_EXE%" run -d --rm --name book-store-test -p 18080:5000 "%DOCKER_IMAGE%"
                        '''

                        powershell '''
                            $ErrorActionPreference = "Stop"
                            $ready = $false

                            for ($i = 0; $i -lt 20; $i++) {
                                try {
                                    $response = Invoke-WebRequest `
                                        -Uri "http://127.0.0.1:18080/" `
                                        -UseBasicParsing `
                                        -TimeoutSec 3

                                    if ($response.StatusCode -eq 200) {
                                        $ready = $true
                                        break
                                    }
                                } catch {
                                    Start-Sleep -Seconds 2
                                }
                            }

                            if (-not $ready) {
                                throw "Book store health check failed."
                            }

                            Write-Output "Book store HTTP test passed."
                        '''
                    } finally {
                        bat '''
                            "%DOCKER_EXE%" stop book-store-test 2>NUL
                            exit /b 0
                        '''
                    }
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-hub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat 'powershell -NoProfile -NonInteractive -Command "$env:DOCKER_PASS | & $env:DOCKER_EXE login --username $env:DOCKER_USER --password-stdin"'

                    bat '"%DOCKER_EXE%" push "%DOCKER_IMAGE%"'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kuberconfig',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    bat '''
                        set "KUBECONFIG=%KUBECONFIG_FILE%"

                        "%KUBECTL_EXE%" get nodes --request-timeout=15s

                        "%KUBECTL_EXE%" apply -f deployment.yaml

                        "%KUBECTL_EXE%" rollout status deployment/online-book-store --timeout=180s

                        "%KUBECTL_EXE%" get deployments
                        "%KUBECTL_EXE%" get pods
                        "%KUBECTL_EXE%" get services
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Build, test, push and Kubernetes deployment completed.'
        }
        failure {
            echo 'FAILED: Check the first failing stage and its error in the console log.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
