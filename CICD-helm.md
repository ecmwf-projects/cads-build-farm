# CI/CD HelmChart Pipeline Documentation

This document describes the automation logic for the Helm chart pipeline, taking the **dss-broker-chart** as an example.  

The pipeline is designed to automate the release process starting from a PR or push on the source code, in order to **build** and **release** a Helm chart to the registry with the corresponding **tag**, and automatically handle merge operations when appropriate.  

---

## Table of Contents
- [Pipeline Overview](#pipeline-overview)
- [Workflow Steps](#workflow-steps)
- [Parameters and Secrets](#parameters-and-secrets)

---

## Pipeline Overview
The pipeline consists of **two interconnected workflows**:

- **Calling Workflow (in this case from the dss-broker chart `.github/workflows/main.yaml`)**  
  Acts as the entry point of the pipeline.  
  It defines the events that trigger the process (push, pull request, manual dispatch) and calls a generic reusable workflow to build and publish the Helm chart.  

  Example configuration for the **dss-broker-chart**:
  This pipline has two jobs, `build_helm_chart` resposable to build tag and push the helm chart and the `auto_merge` that will be trigger each time a PR passed without the need to manually close the PR opened.

  The `auto_merge` is a sequence of API call againts github with the correct DSS_HELM PAT in order to performe action as merging and open PR.

  ```yaml
  name: Build dss-broker-chart

  on:
    workflow_dispatch:
    push:
      branches:
        - main
      tags:
        - "v*"
    pull_request:
      branches:
        - main

  jobs:
    build_helm_chart:
      name: Build helm chart
      uses: ecmwf-projects/cads-build-farm/.github/workflows/helm-chart.yaml@main
      secrets:
        ECMWF_DOCKER_REGISTRY_USERNAME: ${{ secrets.ECMWF_DOCKER_REGISTRY_USERNAME }}
        ECMWF_DOCKER_REGISTRY_ACCESS_TOKEN: ${{ secrets.ECMWF_DOCKER_REGISTRY_ACCESS_TOKEN }}

    auto_merge:
      needs: build_helm_chart
      uses: ecmwf-projects/cads-build-farm/.github/workflows/helm-chart-automerge.yaml@helm-chart-pipeline
      secrets:
        DSS_HELM_PAT: ${{ secrets.DSS_HELM_PAT }}
  ```



- **Called Workflow (`helm-chart.yaml`), located in `cads-build-farm/workflows/helm-chart.yaml`**  
  This is the **core** of the pipeline.  
  Works as a **modular template** that encapsulates the standardized logic for:
  - packaging the Helm chart  
  - versioning  
  - pushing the chart to the container registry  

  Example definition:

  ```yaml
  name: 'Helm build tag and push'
  description: 'Package a Helm Chart and push on a container registry'

  on:
    workflow_call:
      secrets:
        ECMWF_DOCKER_REGISTRY_USERNAME:
          required: true
        ECMWF_DOCKER_REGISTRY_ACCESS_TOKEN:
          required: true
  ```

---

## Workflow Steps

The associated steps perform the following:

- **Checkout chart-repo**  
  Checks out the calling repository (in this case, the Helm chart repo `dss-broker-chart`).

- **Compute semantic version**  
  Calculates the chart version from Git history using `git-version`.

- **Replace chart version**  
  Updates the `Chart.yaml` file with the computed version.  
  Example:  
  ```yaml
  version: 1.2.3
  ```

- **Set Helm Chart Variables**  
  Extracts chart metadata (name, version, output folder) and sets them as environment variables.  
  Outputs:  
  ```yaml
  HELM_CHART_NAME: the name of the chart
  HELM_CHART_VERSION: the computed version of the helm chart itself
  output-folder: temporary folder containing chart artifacts
  ```

- **Helm build**  
  Packages the chart locally using `helm package`.  
  Authentication is performed against the target registry using the provided secrets.

- **Helm push**  
  Pushes the packaged chart to the OCI registry (`oci://eccr.ecmwf.int/cads/helm`).  
  This step is skipped when the event is a pull request.

- **Cleanup**  
  Removes temporary build artifacts created during the process.

---

## Parameters and Secrets

### Calling Workflow → Called Workflow

| Name                              | Type    | Description                                                                 |
|-----------------------------------|---------|-----------------------------------------------------------------------------|
| `ECMWF_DOCKER_REGISTRY_USERNAME`  | Secret  | Username to authenticate against the ECMWF container registry.              |
| `ECMWF_DOCKER_REGISTRY_ACCESS_TOKEN` | Secret | Access token to authenticate against the ECMWF container registry.          |
| `DSS_HELM_PAT`                    | Secret  | Github token used by the automerge job for Helm chart repositories.|

### Environment Variables (set in Called Workflow)

| Name               | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `registryUrl`      | URL of the container registry (e.g., `https://eccr.ecmwf.int`).             |
| `helmRegustryUrl`  | Hostname of the Helm registry (`eccr.ecmwf.int`).                          |
| `registryUsername` | The registry username, mapped from `ECMWF_DOCKER_REGISTRY_USERNAME`.        |
| `registryPassword` | The registry access token, mapped from `ECMWF_DOCKER_REGISTRY_ACCESS_TOKEN`.|
