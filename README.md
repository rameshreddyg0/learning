<div id="top"></div>
<!-- TABLE OF CONTENTS -->
    <summary>Table of Contents</summary>
    <ol>
        <li><a herf="#about-the-solution">About The Solution</a></li>
        <li>
            <a herf="#getting-started">Getting Started</a>
            <ul>
                <li><a herf="#components">Components</a></li>
                <li><a herf="#prerequisites">Prerequisites</a></li>
            </ul>
        </li>    
        <li>
            <a herf="#repo-constituents">Repo-Constituents</a>
            <ul>
                <li><a herf="#gcp">gcp</a></li>
                <li><a herf="#governance">governance</a></li>
                <li><a herf="#scripts">scripts</a></li>
                <li><a herf="#codeowners-file">CODEOWNERS file</a></li>
                <li><a herf="#jenkinsfile">Jenkinsfile</a></li>
                <li><a herf="#deploymentPropeertiesjson-file">deploymentProperties.json file</a></li>
                <li><a herf="#sonar-projectproperties">sonar-project.properties</a></li>
            </ul>
        </li>
        <li><a herf="#contact">Contact</a></li>
        <li><a herf="#references">References</a></li>
    </ol>

<!-- About The Solution -->
## About The Solution
The solution is designed to handle security policy deployment across cloud platforms. Currently the solution would be catering to deploying sentinel, native & prisma security policies for GCP, AWS & Azure cloud platforms. Details specific to each policy type for each cloud provider has been documented below:

| Sr.No | Security Policy Type | Cloud Provider | Reference Link                               |
|:-----:|:--------------------:|:--------------:|:--------------------------------------------:|
|   1   | Sentinel             | GCP            |[sentinel GCP README](gcp/sentinel/README.md) |
|   2   | Native               | GCP            |[native GCP README](gcp/native/README.md)     |
|   3   | Prisma               | GCP            |[prisma GCP README](gcp/prisma/README.md)     |
