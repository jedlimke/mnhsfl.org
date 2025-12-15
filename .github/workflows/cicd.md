sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub Actions<br/>Runner
    participant Test as Test Job
    participant Build as Build Job
    participant Deploy as Deploy Job
    participant Pages as GitHub Pages

    Dev->>GH: Push to master branch
    GH->>Test: Trigger workflow
    rect rgb(225, 245, 255)
        Note over Test: TEST JOB
        Test->>Test: Checkout code
        Test->>Test: Setup Python 3.11
        Test->>Test: Install pytest
        Test->>Test: Run 12 integration tests
        Test->>Test: Generate results from fixtures
        Test->>Test: Verify posts created
    end
    alt Tests Pass ✅
        Test->>Build: Continue to build
        
        rect rgb(255, 243, 205)
            Note over Build: BUILD JOB
            Build->>Build: Checkout code
            Build->>Build: Setup Pages
            Build->>Build: Setup Python 3.13
            Build->>Build: Convert and build<br />fencing results
            Build->>Build: Build Jekyll site
            Build->>Build: Upload site artifact
        end
        
        alt Build Success ✅
            Build->>Deploy: Continue to deploy
            
            rect rgb(212, 237, 218)
                Note over Deploy: DEPLOY JOB
                Deploy->>Pages: Deploy site artifact
                Pages-->>Deploy: Deployment complete
            end
            
            Deploy-->>Dev: ✅ Site live!
        else Build Fails ❌
            Build-->>Dev: ❌ Build failed - no deploy
        end
        
    else Tests Fail ❌
        Test-->>Dev: ❌ Tests failed - build & deploy cancelled
    end