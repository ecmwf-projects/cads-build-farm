# CI/CD Pipeline Documentation

This document describes the automation logic for the pipelines, taking the **cads-broker** service and its related Python packages as an example.  

The pipeline is designed to automate the release process starting from a PR on the source code, in order to **build** and **release** a Docker image for the source repository with the corresponding **tag**, and automatically trigger the creation of the associated **Helm chart**.  

---

## Table of Contents
- [Pipeline Overview](#pipeline-overview)
- [Triggers and Workflow](#triggers-and-workflow)
- [Workflow Steps](#workflow-steps)

---

## 🏗️ Pipeline Overview
The pipeline consists of **two interconnected workflows**:

- **Calling Workflow (in this case from the cads-broker code `.github/workflow/main.yaml`)**  
  Acts as the entry point of the pipeline.  
  It defines the events that trigger the process (push, pull request, etc.) and calls a generic reusable workflow, passing it the specific parameters for the `cads-broker` service.

  Parameters used for the **cads-broker** service:

  ```yaml
  jobs:
    build_docker_image:
      name: Build docker image
      uses: ecmwf-projects/cads-build-farm/.github/workflows/docker-build.yaml@main
      with:
        dockerfile: 'Broker.Dockerfile'
        chart-repo: 'ecmwf/dss-broker-chart'
        package-ref: "CADS_BROKER_REF"
        repositories: |
          ecmwf-projects/cads-worker
          ecmwf-projects/cads-processing-api-service
      secrets: inherit
  ```

  **Parameter Description:**

  | Parameter      | Description                                                                 |
  |----------------|-----------------------------------------------------------------------------|
  | `dockerfile`   | The specific Dockerfile of the code, always prefixed with the repo name (in this case `Broker.Dockerfile`) used to build the image. |
  | `chart-repo`   | The associated Helm Chart repository to be updated with the newly released version. |
  | `package-ref`  | The associated Python package that will be updated **only with stable tags**. |
  | `repositories` | List of repositories dependent on the Python package that will receive the update via an automatic PR. |
  | `secrets`      | Defines how secrets are inherited from the calling workflow. |

- **Called Workflow (`docker-build.yaml`), located in `cads-build-farm/workflows/docker-build.yaml`**  
  It is the **core** of the pipeline.  
  Works as a **modular template** that encapsulates the standardized logic for:
  - building the Docker image  
  - tagging  
  - pushing to the registry  

  It is dynamically configured through the parameters passed by the calling workflow.

---

## 🔄 Workflow Steps

The associated steps perform the following:

- **Checkout code-repo**  
  checks out the calling repository (in this case, the broker code)

- **Checkout cads-build-farm**  
  checks out the `cads-build-farm` repository to copy a set of scripts contained in the `scripts/` folder

- **Copy all shared scripts to root**  
  copies the shared scripts into the root directory

- **Compute semantic version**  
  calculates the version using `gitversion`

- **Login to harbor registry**  
  authenticates against the Harbor registry

- **Image variables**  
  extracts variables such as the image name and version that will be used later

- **Debug image variables**  
  simple debug output of the previously created variables

- **Dockerfile build tag and push**  
  performs the actual build, tag, and push of the Docker image

- **Update HelmChart**  
  automates the PR for the related Helm Chart (in this case `dss-broker`)

- **Update Related Python Packages**  
  if the built image has been tagged with a stable semVer, the related Python packages will be updated with an automatic PR.

---