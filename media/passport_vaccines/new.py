import os
import json
import requests
import zipfile
import xml.etree.ElementTree as ET
from jenkinsapi.jenkins import Jenkins
# from rich import print as rprint
import streamlit as st
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_community.llms import Ollama
from langchain_core.tools import tool


# ------------------ Downloading Artifacts ------------------

# Jenkins Credentials and URLs
jenkins_url = "https://engci-jenkins-blr.cisco.com/jenkins/job/team_opticalcontroller-tunerapp-jenkins/job/onc-capp/job/Sanity"
jenkins_base_url = "https://engci-jenkins-blr.cisco.com/jenkins/"
username = "chethrao"
password = "1109079bcafb6239556bdade07ed5f524d"
job_name = "team_opticalcontroller-tunerapp-jenkins/onc-capp/Sanity/Nightly-25.1.1"

# Directory setup
download_dir = "downloaded_artifacts"
extracted_dir = os.path.join(download_dir, "extracted_files")
zip_dir = os.path.join(download_dir, "zip_files")
os.makedirs(download_dir, exist_ok=True)
os.makedirs(extracted_dir, exist_ok=True)
os.makedirs(zip_dir, exist_ok=True)

class Download_Artifacts:

    def get_build_number(self, jenkins_url, jobname, username, password):
        """Get the latest build number."""
        J = Jenkins(jenkins_url, username, password)
        job = J[jobname]
        lb = job.get_last_build()
        print(lb)
        return lb.get_number()
        
    def connect_to_jenkins(self):
        """Establish connection to Jenkins."""
        return Jenkins(jenkins_base_url, username=username, password=password)

    def download_and_extract_artifacts(self, build, build_number):
        """Download and extract artifacts for the specified build."""
        artifacts = list(build.get_artifacts())
        if not artifacts:
            print("No artifacts found in the build.")
            return []

        print(f"Found {len(artifacts)} artifact(s).")
        downloaded_artifacts = []

        for artifact in artifacts:
            artifact_url = artifact.url
            artifact_name = artifact.filename
            artifact_name = artifact_name.replace(":", "_")
            artifact_path = os.path.join(download_dir, artifact_name)
            
            print(f"Downloading {artifact_name} from {artifact_url}")
            try:
                response = requests.get(artifact_url, auth=(username, password), stream=True)
                response.raise_for_status()
                with open(artifact_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                
                file_size = os.path.getsize(artifact_path)
                print(f"{artifact_name} downloaded successfully, file size: {file_size} bytes.")

                if artifact_name.endswith('.zip') and file_size > 0:
                    zip_file_path = os.path.join(zip_dir, artifact_name)
                    os.rename(artifact_path, zip_file_path)
                    specific_extract_dir = os.path.join(extracted_dir, artifact_name.replace('.zip', ''))
                    os.makedirs(specific_extract_dir, exist_ok=True)

                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(specific_extract_dir)
                    print(f"{artifact_name} unzipped successfully into {specific_extract_dir}.")

                    downloaded_artifacts.append(specific_extract_dir)
                else:
                    print(f"{artifact_name} is not a zip file or has no content.")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading artifact {artifact_name}: {e}")

        return downloaded_artifacts
    
    def extract_artifacts(self):
        build_number = self.get_build_number(jenkins_url,"Nightly-25.1.1", username, password)
        if build_number is None:
            return

        # Step 2: Connect to Jenkins and get the job
        jenkins = self.connect_to_jenkins()
        job = jenkins[job_name]
        
        # Step 3: Get the build details and download artifacts
        build = job.get_build(build_number)
        print(f"Build Status: {build.get_status()}")

        # Step 4: Download and extract artifacts
        extracted_dirs = self.download_and_extract_artifacts(build, build_number)
        return extracted_dirs


# ------------------ Build Summary ------------------

class BuildSummary:
    def parse_results_summary(self, specific_extract_dir):
        """Parse 'ResultsSummary.xml' from extracted directories and collect data."""
        Build_Results = []

        for root, dirs, files in os.walk(specific_extract_dir):
            for file in files:
                if file == 'ResultsSummary.xml':
                    xml_path = os.path.join(root, file)
                    print(f"Processing ResultsSummary.xml at {xml_path}")

                    try:
                        tree = ET.parse(xml_path)
                        xml_root = tree.getroot()
                        job_summary = {
                            "Job Name": xml_root.find("jobName").text,
                            "Aborted": xml_root.find("aborted").text,
                            "Passed": xml_root.find("passed").text,
                            "PassX": xml_root.find("passx").text,
                            "Failed": xml_root.find("failed").text,
                            "Blocked": xml_root.find("blocked").text,
                            "Skipped": xml_root.find("skipped").text,
                            "Errored": xml_root.find("errored").text,
                            "Unknown": xml_root.find("unknown").text,
                            "Never Ran": xml_root.find("never_ran").text,
                            "Total": xml_root.find("total").text,
                            "Success Rate": xml_root.find("success_rate").text,
                            "Start Time": xml_root.find("starttime").text,
                            "Stop Time": xml_root.find("stoptime").text,
                        }
                        Build_Results.append(job_summary)
                    except ET.ParseError as e:
                        print(f"Error parsing {xml_path}: {e}")

        return Build_Results

    def extracted_summary(self, extracted_dirs):
        """Parse ResultsSummary.xml files from each extracted directory."""
        Build_Results = []
        for dir_path in extracted_dirs:
            summaries = self.parse_results_summary(dir_path)
            Build_Results.extend(summaries)
        
        # Display build results
        print("\nFinal Build Results Summary:")
        for summary in Build_Results:
            print("\nJob Summary:")
            for key, value in summary.items():
                print(f"{key}: {value}")
                return summary


# ------------------ Failure Handling ------------------

class xml_parser:

    def get_tree_from_path(self, file_path):
        """Parse XML file from the provided file path."""
        return ET.parse(file_path)
   
    def get_root_from_tree(self, tree):
        """Get the root of the XML tree."""
        return tree.getroot()
   
    def get_job_node(self, root):
        """Find the job execution node within the XML structure."""
        test_suite_node = root.find("{http://wwwin-ats.cisco.com/xml/schema/aereport}testsuite")
        job_node = test_suite_node.find("{http://wwwin-ats.cisco.com/xml/schema/aereport}jobexecution")
        return job_node

    def get_testscripts(self, job_node):
        """Get all the test scripts under the job node."""
        return job_node.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}testscript')

    def get_testcases(self, testscript_node):
        """Get all test cases within a test script node."""
        return testscript_node.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}testcase')

    def is_failure(self, node):
        """Check if a given node indicates a failure based on the result."""
        result = node.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}result').text
        return result != 'passed'

    def get_logs(self, node):
        """Extract and return the logs for a failed test step or section."""
        logfile_node = node.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}logfile')
        if logfile_node is not None:
            logfile_attribs = logfile_node.attrib
            begin = int(logfile_attribs['begin'])
            end = int(logfile_attribs['size'])
            logfile_name = logfile_node.text
            log_file_path = os.path.join(os.getcwd(),'downloaded_artifacts','extracted_files', 
                                         'onc_25.1.1_nightly_cosm.2024Nov07_20_56_23.687902',
                                           logfile_name)
            
            try:
                with open(log_file_path, 'rb') as file:
                    file.seek(begin)
                    data = file.read(end)
                return data.decode("ascii")
            except Exception as e:
                return f"Error reading log file: {e}"
        return None
    
    def process_step(self, step):
        """Process a single step in a test case or section."""
        if self.is_failure(step):
            log = self.get_logs(step)
            return log
        return None

    def process_section(self, section):
        """Process a section in a test case, handle failures and steps."""
        logs = []
        if self.is_failure(section):
            log = self.get_logs(section)
            if log:
                logs.append(log)
        
        steps = section.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}step')
        for step in steps:
            log = self.process_step(step)
            if log:
                logs.append(log)
        return logs

    def get_testcase_fail_info(self, test_case):
        """Extract failure info for each test case."""
        logs = []
        sections = test_case.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}section')
        for section in sections:
            section_logs = self.process_section(section)
            logs.extend(section_logs)
        return 
    def get_steps(self, section):
        """Get all steps for a given section."""
        steps = section.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}step')
        return steps if steps else None
     
    def get_name(self, node): 
        """Extract and return the name of the node."""
        name = node.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}name').text
        return name
    
    def get_tc_name(self, test_case):
        """Extractand return the name of the testcase name"""
        initinfo_node = test_case.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}initinfo')
        if initinfo_node is not None:
            name_node = initinfo_node.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}name')
            if name_node is not None:
                tc_name = name_node.text
        return tc_name
    
    def get_testscript_name(self, test_script):
        """Extract and return the name of the test script."""
        initinfo_node = test_script.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}initinfo')
        if initinfo_node is not None:
            taskid_node = initinfo_node.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}taskid')
            if taskid_node is not None:
                return taskid_node.text.strip()
        return "Unnamed Script"  
    
    def get_common_setup_info(self, test_script):
        """Collect common setup failure info for a test script."""
        commonsetup = test_script.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}commonSetup')
        subsection_failures_setup = []
        if commonsetup is not None:
            if self.is_failure(commonsetup):
           
                sub_sections_setup = commonsetup.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}subSection')
                step_failures = []
                if sub_sections_setup:
                    for sub_section_setup  in sub_sections_setup:
                        subsection_name_setup = self.get_name(sub_section_setup)
        
                        if self.is_failure(sub_section_setup):
                            steps = self.get_steps(sub_section_setup)
                                
                            if steps:
                                for step in steps:
                                    if self.is_failure(step):  
                                        step_name = self.get_name(step)
                                        step_log = self.get_logs(step)
                                        step_failures.append({
                                            "Subsection": subsection_name_setup,
                                            "Step Name": step_name,
                                            "Failure Logs": step_log
                                        })
                            
                
                                subsection_log = self.get_logs(sub_section_setup)
                                subsection_failures_setup.append({
                                    "Subsection Name": subsection_name_setup,
                                    "Subsection Logs": subsection_log,
                                    "Steps": step_failures
                                })
                            else:
                                subsection_log = self.get_logs(sub_section_setup)
                                subsection_failures_setup.append(
                                    {
                                    "Subsection Name": subsection_name_setup,
                                    "Subsection Logs": subsection_log  
                                    }
                                )

                        
        return subsection_failures_setup 
    
    def get_common_cleanup_info(self, test_script):
        """Collect common cleanup failure info for a test script."""
        commoncleanup = test_script.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}commonCleanup')
        subsection_failures_cleanup = []

        if commoncleanup is not None:
            if self.is_failure(commoncleanup):
           
                sub_sections_cleanups = commoncleanup.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}subSection')
                step_failures = []
                if sub_sections_cleanups:
                    for sub_section_cleanup  in sub_sections_cleanups:
                        subsection_name_cleanup = self.get_name(sub_section_cleanup)
        
                        if self.is_failure(sub_section_cleanup):
                            steps = self.get_steps(sub_section_cleanup)
                                
                            if steps:
                                for step in steps:
                                    if self.is_failure(step):  
                                        step_name = self.get_name(step)
                                        step_log = self.get_logs(step)
                                        step_failures.append({
                                            "Subsection": subsection_name_cleanup,
                                            "Step Name": step_name,
                                            "Failure Logs": step_log
                                        })
                            
                            
                                subsection_log = self.get_logs(sub_section_cleanup)
                                subsection_failures_cleanup.append({
                                    "Subsection Name": subsection_name_cleanup,
                                    "Subsection Logs": subsection_log,
                                    "Steps": step_failures
                                })

                            else:
                                subsection_log = self.get_logs(sub_section_cleanup)
                                subsection_failures_cleanup.append(
                                    {
                                    "Subsection Name": subsection_name_cleanup,
                                    "Subsection Logs": subsection_log
                                    }
                                )

                        
        return subsection_failures_cleanup 
    
    
    def get_setup_info(self,test_case):
        """Collect setup failure info for a testcase."""
        setup = test_case.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}setup')
        setup_failures = []
        if setup is not None and self.is_failure(setup):
               
                    setup_name = self.get_name(setup)
                    setup_logs = self.get_logs(setup)
                    setup_failures.append(
                        {
                            "Setup Name": setup_name,
                            "Setup Logs": setup_logs
                        }
                    )
        return setup_failures 
    

    def get_testcase_fail_info(self, test_case, Failure_logs=False):    
        """Extract failure information for a given test case."""
        failure_info = {}
        tc_name = 'Unknown'
            
        initinfo_node = test_case.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}initinfo')


        tc_name = self.get_tc_name(test_case)
        failure_info['Testcase Name'] = tc_name

        # Check if the entire test case has failed
        if self.is_failure(test_case) and Failure_logs:
            setup_info = self.get_setup_info(test_case)
            if setup_info:
                failure_info['Setup_Failure'] = setup_info

            sections = test_case.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}section')
            section_failures = [] 
            if sections:
                for section in sections:
                    if self.is_failure(section):
                        step_failures = [] 
                        steps = self.get_steps(section)
                        section_name = self.get_name(section)
                        
                        if steps:
                            for step in steps:
                                if self.is_failure(step):
                                    step_name = self.get_name(step)
                                    step_log = self.get_logs(step)
                                    step_failures.append(
                                        {
                                            "Step Name": step_name,
                                            "Failure Logs": step_log
                                        }
                                    )
                                    
                            section_failures.append(
                                {
                                    "Section Name": section_name,
                                    "Steps": step_failures 
                                }
                            )
                        else:
                            # section failure without steps
                            section_log = self.get_logs(section)
                            section_failures.append(
                                {
                                    "Section Name": section_name,
                                    "Section Logs": section_log 
                                }
                            )

            else:
                # Test case fails but has no sections or steps
                testcase_log = self.get_logs(initinfo_node)
                failure_info["Testcase Logs"] = testcase_log

            failure_info["Sections"] = section_failures

            cleanup_info = self.get_cleanup_info(test_case)
            if cleanup_info:
                failure_info['Cleanup_Failure'] = cleanup_info
                # print("failure info:",failure_info)

            return failure_info
        
        
        return {"Status": f"{tc_name} - No failure"}
    
    def get_fail_testcase_name(self, test_case):
        if self.is_failure(test_case):
            tc_name = self.get_tc_name(test_case)
            return tc_name
    
    def get_cleanup_info(self, test_case):
        """Collect cleanp failure info for a test case."""
        cleanup = test_case.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}cleanup')
        cleanup_failures = []

        if cleanup is not None and self.is_failure(cleanup):
            sections = cleanup.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}section')

            # If cleanup has sections 
            if sections:
                step_failures = []
                for section in sections:
                    if self.is_failure(section):
                        steps = self.get_steps(section)
                        section_name = self.get_name(section)
                        section_logs = self.get_logs(section)
             
                        # Collect failed steps within the section
                        if steps:
                            for step in steps:
                                if self.is_failure(step):
                                    step_name = self.get_name(step)
                                    step_log = self.get_logs(step)
                                    step_failures.append({
                                        "Step Name": step_name,
                                        "Failure Logs": step_log
                                    })

                        cleanup_failures.append({
                            "Section Name": section_name,
                            "Section Logs": section_logs,
                            "Steps": step_failures if step_failures else None
                        })

            #If cleanup has no sections but does have steps
            else:
                steps = self.get_steps(cleanup)
                step_failure_info = []
                if steps:
                    for step in steps:
                        if self.is_failure(step):
                            step_name = self.get_name(step)
                            step_log = self.get_logs(step)
                            step_failure_info.append({
                                "Step Name": step_name,
                                "Failure Logs": step_log
                            })
                
                # Only append if there are step failures
                if step_failure_info:
                    cleanup_failures.append({
                        "Steps": step_failure_info
                    })

            #If cleanup has no sections and no steps but fails
            if not sections and not steps:
                cleanup_log = self.get_logs(cleanup)
                cleanup_failures.append({
                    "Cleanup Logs": cleanup_log
                })

        return cleanup_failures

    
    def extract_logs(self, svo_result_file):
        tree = self.get_tree_from_path(svo_result_file)
        root = self.get_root_from_tree(tree)
        job_node = self.get_job_node(root)
        test_scripts = self.get_testscripts(job_node)

        logs_text = ""

        for test_script in test_scripts:
            # Retrieve common setup failure logs
            common_setup_failures = self.get_common_setup_info(test_script)
            if common_setup_failures:
                logs_text += "\n" + "--" * 20 + "\n" + json.dumps({"CommonSetupFailures": common_setup_failures}, indent=4)

            # Retrieve individual test case failure logs
            test_cases = self.get_testcases(test_script)
            for test_case in test_cases:
                failure_info = self.get_testcase_fail_info(test_case)
                logs_text += "\n" + "--" * 20 + "\n" + json.dumps(failure_info, indent=4)

            # Retrieve common cleanup failure logs
            common_cleanup_failures = self.get_common_cleanup_info(test_script)
            if common_cleanup_failures:
                logs_text += "\n" + "--" * 20 + "\n" + json.dumps({"CommonCleanupFailures": common_cleanup_failures}, indent=4)
        print("logs_text",logs_text)
        return logs_text 

import re
class testcasename(xml_parser):
    def __init__(self):
        super().__init__()

    def get_fail_testcase_name(self, test_case):
        """Check if the test case failed and return the name if it did."""
        if self.is_failure(test_case):
            tc_name = self.get_tc_name(test_case)
            return tc_name
        return None
    
    def get_description(self, test_case):
        """Extract description of testcases"""
        initinfo_node = test_case.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}initinfo')
        if initinfo_node is not None:
            description_node = initinfo_node.find('{http://wwwin-ats.cisco.com/xml/schema/aereport}description')
        if description_node is not None:
            description = description_node.text
        return description
    

    def extract_names(self, svo_result_file, failure_logs=None, description=None, author=None):
        """
        Extract names of failed test cases grouped under their corresponding test scripts.
        """
        tree = self.get_tree_from_path(svo_result_file)
        root = self.get_root_from_tree(tree)
        job_node = self.get_job_node(root)
        test_scripts = self.get_testscripts(job_node)

        failed_testcases_by_script = {}

        for test_script in test_scripts:
            script_name = self.get_testscript_name(test_script)  
            failed_testcases = []  

            test_cases = self.get_testcases(test_script)
            for test_case in test_cases:
                if self.is_failure(test_case):  
                    testcase_name = self.get_tc_name(test_case)

                    if failure_logs:
                        failure_info = self.get_testcase_fail_info(test_case)
                        failed_testcases.append({
                            "Testcase Name": testcase_name,
                            "Failure Logs": failure_info
                        })
                    elif description:
                        testcase_desc = self.get_description(test_case)
                        failed_testcases.append({
                            "Testcase": testcase_name,
                            "Description": testcase_desc
                        })

                    elif author:
                        testcase_desc = self.get_description(test_case)

                        # Regex pattern to match authors in flexible formats
                        pattern = r"author\s*:\s*([a-zA-Z0-9_]+(?:\s*(?:,|[-–>&gt;]+)\s*[a-zA-Z0-9_]+)*)"

                        match = re.search(pattern, testcase_desc)

                        if match:
                            # Extract all author names by further splitting if needed
                            raw_authors = match.group(1)
                            author_names = re.findall(r"[a-zA-Z0-9_]+", raw_authors)
                        else:
                            author_names = ["Author not found"]

                        # Append the list of authors to the failed test cases
                        failed_testcases.append({
                            "Testcase": testcase_name,
                            "Authors": author_names
                        })


                    else:
                        failed_testcases.append(testcase_name)

            if failed_testcases:  # Only include scripts with failed test cases
                failed_testcases_by_script[script_name] = failed_testcases

        return failed_testcases_by_script

# ------------------ Section failure ------------------
class SectionInfo(xml_parser):
    def __init__(self):
        super().__init__()

    def get_section_info(self, testcase_name: str, svo_results_file, failure_logs=None):
        """
        Extract section names and optionally include failure logs for a given testcase by its name.
        Parses the XML, locates all test case nodes with the matching name, and gathers section failure information.
        Returns a dictionary containing section names and logs if requested.
        """
        failure_section_info = {}

        try:
            tree = self.get_tree_from_path(svo_results_file)
            root = self.get_root_from_tree(tree)
            job_node = self.get_job_node(root)
            test_scripts = self.get_testscripts(job_node)

            # Iterate through all test scripts and test cases to find matches for testcase_name
            for test_script in test_scripts:
                test_cases = self.get_testcases(test_script)
                for test_case in test_cases:
                    # Match the testcase name
                    if self.get_tc_name(test_case) == testcase_name:
                        # If testcase name matches, gather section info
                        if self.is_failure(test_case):
                            sections = test_case.findall('{http://wwwin-ats.cisco.com/xml/schema/aereport}section')
                            section_failures = []

                            if sections:
                                for section in sections:
                                    if self.is_failure(section):
                                        section_name = self.get_name(section)
                                        # Append only section name if failure_logs=False
                                        if failure_logs==True:
                                            section_log = self.get_logs(section)
                                            section_failures.append({
                                                "section_name": section_name,
                                                "section_logs": section_log
                                            })
                                        else:
                                            section_failures.append({"section_name": section_name})

                            failure_section_info["Sections"] = section_failures

            # No failed sections found
            if not failure_section_info.get("Sections"):
                failure_section_info = {
                    "message": "No failed sections found for the given test case name."
                }

        except Exception as e:
            print(f"Error in fetching section information: {e}")
            failure_section_info = {"error": str(e)}

        return failure_section_info
        
# ------------------ Main Execution ------------------

import operator
from typing import Annotated, TypedDict, Union
from langchain_ollama import OllamaLLM
from langchain.agents import create_react_agent
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain.agents import create_react_agent
from langchain.prompts import PromptTemplate

class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


def main():
    # Initialize dependencies
    download = Download_Artifacts()
    build_summary = BuildSummary()
    logs_tool = xml_parser()
    failed_name = testcasename()
    section_names = SectionInfo()

    # Define tools
    @tool
    def get_summary(query: str = None) -> str:
        """
    Retrieve the build summary from extracted artifacts.

    If the artifacts are not already downloaded, they will be extracted first. 
    Returns the build summary or an error message if retrieval fails.
    """
        try:
            artifacts_dir = "downloaded_artifacts"
            if not os.path.exists(artifacts_dir):
                extracted_dirs = download.extract_artifacts()
            else:
                extracted_dirs = [artifacts_dir]
            summaries = build_summary.extracted_summary(extracted_dirs)
            return f"Build Summary: {summaries}"
        except Exception as e:
            return f"Error in fetching build summary: {e}"

    @tool
    def get_logs(query: str = None) -> str:
        """
    Retrieve failure logs from the specified XML file.

    Input:
    - `query` (str, optional): A string to filter or search the logs.
    Output:
    - A string containing the failure logs, or an error message if retrieval fails.
    
    Use when the user asks for logs or specific details from the build process.
    """
        try:
            svo_results_file = os.path.join(
                "downloaded_artifacts", "extracted_files",
                "onc_25.1.1_nightly_cosm.2024Nov07_20_56_23.687902", "ResultsDetails.xml"
            )
            logs = logs_tool.extract_logs(svo_results_file)
            return f"Build Logs: {logs}"
        except Exception as e:
            return f"Error in fetching logs: {e}"

    @tool
    def get_testcase_name(failure_logs: bool = None, description: bool = None, author: bool = None) -> str:
        """
    Retrieve the test case names of failed test cases, get the failure logs, description, and author if asked.

    Arguments:
    - `failure_logs` (bool, optional): Whether to include failure logs. Default is False.
    - `description` (bool, optional): Whether to include description of test cases. Default is False.
    - `author` (bool, optional): Whether to include author details. Default is False.

    Returns:
    - A string containing the test case names and requested details, or an error message if retrieval fails.
    """
        try:
            # Ensure that boolean values are being passed correctly
            if isinstance(failure_logs, str):
                failure_logs = failure_logs.lower() in ["true", "1"]
            if isinstance(description, str):
                description = description.lower() in ["true", "1"]
            if isinstance(author, str):
                author = author.lower() in ["true", "1"]

            # File path for extracting logs or test case details
            svo_results_file = os.path.join(
                "downloaded_artifacts", "extracted_files",
                "onc_25.1.1_nightly_svo.2024Nov11_15_35_54.262116", "ResultsDetails.xml"
            )

            testcase_names = failed_name.extract_names(
                svo_results_file, failure_logs=failure_logs, description=description, author=author
            )

            if not testcase_names:
                return "No failed test cases found."

            return f"Testcase Failures: {testcase_names}"
        except Exception as e:
            return f"Error in fetching test case names: {e}"

    @tool
    def get_section_name(testcase_name: str, failure_logs: bool = None) -> str:
        """
    Retrieve section names and optionally failure logs for the given test case.

    Arguments:
    - `testcase_name` (str): The name of the test case for which section information is required.
    - `failure_logs` (bool, optional): Whether to include failure logs. Default is False.

    Returns:
    - A string containing the section names and failure logs, or an error message if retrieval fails.
    """
        try:
            if isinstance(failure_logs, str):
                failure_logs = failure_logs.lower() in ["true", "1"]

            svo_results_file = os.path.join(
                "downloaded_artifacts", "extracted_files",
                "onc_25.1.1_nightly_svo.2024Nov11_15_35_54.262116", "ResultsDetails.xml"
            )

            section_details = section_names.get_section_info(
                testcase_name, svo_results_file, failure_logs=failure_logs
            )

            if "Sections" not in section_details:
                return section_details.get(
                    "message",
                    f"Error: {section_details.get('error', 'Unknown error occurred')}"
                )
            return section_details

        except Exception as e:
            return f"Error in fetching section information: {e}"
    
    tools = [get_summary, get_logs, get_testcase_name, get_section_name]
    tool_node = ToolExecutor(tools)

    llm = OllamaLLM(
        base_url="http://10.226.182.75:11434",
        model="qwen2.5:14b-instruct-q8_0",
        request_timeout=300.0,
        temperature=0.0,
        additional_kwargs={"seed": 42, "num_ctx": 32768}
    )

    react_template = """
You are an assistant who uses tools to answer questions and solve tasks.

Tools available:
{tools}

Available tool names: {tool_names}

Instructions:
- Use tools to assist you.
- Always follow this format:
  Action: <tool_name>
  Action Input: <input>
- When responding:
  Final Answer: <your answer>
- Do not include additional explanations unless explicitly asked.

Scratchpad:
{agent_scratchpad}

Query:
{input}
"""

    prompt_template = PromptTemplate(
        input_variables=["input", "tools", "agent_scratchpad", "tool_names"],
        template=react_template
    )

    agent_runnable = create_react_agent(llm, tools, prompt_template)

    def execute_tools(state):
        try:
            action: AgentAction = state["agent_outcome"]
            print(f"Executing tool: {action.tool} with input: {action.tool_input}")
            
            response = tool_node.invoke(ToolInvocation(tool=action.tool, tool_input=action.tool_input))
            print(f"Tool Response: {response}")

            if "Final Answer" in response:
                print(f"Final Answer from LLM: {response}")
            
            return {"intermediate_steps": [(action, response)]}
        except Exception as e:
            print(f"Error during tool execution: {e}")
            return {"intermediate_steps": []}

    def should_continue(state):
        """
        Decide whether the agent should continue based on the state.
        """
        if "agent_outcome" not in state or state["agent_outcome"] is None:
            print("Error: 'agent_outcome' not found in the state or is None")
            return "end"
        
        action = state["agent_outcome"]
        
        # Check if it's an AgentAction and has a tool attribute
        if isinstance(action, AgentAction) and hasattr(action, "tool"):
            print(f"Action Tool: {action.tool}, Action Input: {action.tool_input}")
            return "continue"
        
        print("Error: 'agent_outcome' does not contain 'tool' attribute")
        return "end"


        
    def run_agent(state):
        """
        Runs the REACT agent to decide what action to take and set the agent outcome in the state.
        """
        try:
            agent_outcome = agent_runnable.invoke(state)
            print(f"LLM Response: {agent_outcome}")  # Log the raw response from the LLM
            
            # Ensure agent_outcome has the expected structure
            if not isinstance(agent_outcome, (AgentAction, AgentFinish)):
                print("Error: Invalid agent_outcome structure.")
                print(f"Agent Outcome: {agent_outcome}")
                state["agent_outcome"] = None
                return state
            
            state["agent_outcome"] = agent_outcome
            return state
        except Exception as e:
            print(f"Error in running agent: {e}")
            state["agent_outcome"] = None
            return state



    workflow = StateGraph(AgentState)
    workflow.add_node("agent", run_agent)  
    workflow.add_node("action", execute_tools)  
    workflow.set_entry_point("agent") 
    workflow.add_conditional_edges(
        "agent", should_continue, {"continue": "action", "end": END} 
    )
    workflow.add_edge("action", "agent")  


    app = workflow.compile()

    input_text = "Provide me the build summary of last build"
    inputs = {"input": input_text, "chat_history": []}

    results = []
    for state in app.stream(inputs):  
        result = list(state.values())[0]
        results.append(result)
        print(f"Step Result: {result}")

if __name__ == "__main__":
    main()
