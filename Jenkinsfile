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

    stage('Install Frontend Dependencies') {
      steps {
        dir('Frontend') {
          echo "Installing Frontend dependencies..."
          bat 'npm install'
        }
      }
    }

    stage('Frontend Lint') {
      steps {
        dir('Frontend') {
          echo "Running Frontend linting (warnings only)..."
          bat 'npm run lint || true'
        }
      }
    }

    stage('Frontend Unit Tests') {
      steps {
        dir('Frontend') {
          echo "Running Frontend unit tests with Vitest..."
          bat 'npm run test:unit'
        }
      }
    }

    stage('Frontend Build') {
      steps {
        dir('Frontend') {
          echo "Building Frontend..."
          bat 'npm run build'
        }
      }
    }

    stage('Check Python Availability') {
      steps {
        script {
          try {
            bat 'python --version'
            env.PYTHON_AVAILABLE = 'true'
            echo "✓ Python is available - Backend tests will run"
          } catch (Exception e) {
            env.PYTHON_AVAILABLE = 'false'
            echo "⚠ Python not available - Backend tests will be skipped"
          }
        }
      }
    }

    stage('Backend Setup') {
      when {
        expression { env.PYTHON_AVAILABLE == 'true' }
      }
      steps {
        dir('Backend') {
          echo "Setting up Python virtual environment..."
          bat '''
            python -m venv venv
          '''
        }
      }
    }

    stage('Backend Unit Tests') {
      when {
        expression { env.PYTHON_AVAILABLE == 'true' }
      }
      steps {
        dir('Backend') {
          echo "Running Backend unit tests with pytest..."
          bat '''
            call venv\\Scripts\\activate.bat
            pip install -q -r requirements.txt
            pytest tests\\unit -v --tb=short
          '''
        }
      }
    }

    stage('Backend Integration Tests') {
      when {
        expression { env.PYTHON_AVAILABLE == 'true' }
      }
      steps {
        dir('Backend') {
          echo "Running Backend integration tests..."
          bat '''
            call venv\\Scripts\\activate.bat
            pytest tests\\integration -v --tb=short
          '''
        }
      }
    }
  }

  post {
    always {
      script {
        if (env.PYTHON_AVAILABLE == 'true') {
          echo "Pipeline completed - Frontend + Backend tests ran"
        } else {
          echo "Pipeline completed - Frontend tests ran (Backend skipped: Python not available)"
        }
      }
    }

    success {
      echo "✓ All available tests passed successfully"
    }

    failure {
      echo "✗ Pipeline failed - check logs above"
    }

    cleanup {
      cleanWs()
    }
  }
}
