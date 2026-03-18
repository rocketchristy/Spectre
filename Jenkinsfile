pipeline {
  agent any

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  environment {
    NODEJS_VERSION = '22'
    PYTHON_VERSION = '3.11'
  }

  stages {
    stage('Checkout') {
      steps {
        echo "Checking out code from repository..."
        checkout scm
      }
    }

    stage('Frontend Tests') {
      parallel {
        stage('Install Dependencies') {
          steps {
            dir('Frontend') {
              echo "Installing Frontend dependencies..."
              sh 'npm install'
            }
          }
        }

        stage('Backend Setup') {
          steps {
            dir('Backend') {
              echo "Setting up Python virtual environment..."
              sh '''
                python -m venv venv || true
                . venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
              '''
            }
          }
        }
      }
    }

    stage('Linting') {
      parallel {
        stage('Frontend Lint') {
          steps {
            dir('Frontend') {
              echo "Running Frontend linting..."
              sh 'npm run lint'
            }
          }
        }
      }
    }

    stage('Unit Tests') {
      parallel {
        stage('Frontend Unit Tests') {
          steps {
            dir('Frontend') {
              echo "Running Frontend unit tests with Vitest..."
              sh 'npm run test:unit'
            }
          }
        }

        stage('Backend Unit Tests') {
          steps {
            dir('Backend') {
              echo "Running Backend unit tests with pytest..."
              sh '''
                . venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
                pip install -q -r requirements.txt
                pytest tests/unit -v
              '''
            }
          }
        }
      }
    }

    stage('Integration Tests') {
      steps {
        dir('Backend') {
          echo "Running Backend integration tests..."
          sh '''
            . venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
            pytest tests/integration -v
          '''
        }
      }
    }

    stage('Build') {
      steps {
        dir('Frontend') {
          echo "Building Frontend..."
          sh 'npm run build'
        }
      }
    }
  }

  post {
    always {
      echo "Pipeline completed"
    }

    success {
      echo "✓ All tests passed successfully"
    }

    failure {
      echo "✗ Pipeline failed - check logs above"
    }

    cleanup {
      cleanWs()
    }
  }
}
