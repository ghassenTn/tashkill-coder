import os
import shutil
import subprocess
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP('tashkil_mcp_server')

@mcp.tool('tashkil-create-react-project')
def tashkil_create_react_project(
    project_name: str,
    path: str = os.getenv('TARGET_FOLDER_PATH')
) -> Dict[str, Any]:
    """
    Copy a prebuilt React parent project into the specified directory
    and rename the folder to the given project name.
    The new project will contain all the components ui (button, toast, etc.)

    Args:
        project_name: Name of the new project
        path: Directory path where the project should be created
    
    Returns:
        Project creation status
    """
    PARENT_PROJECT_PATH = os.getenv('PARENT_PROJECT_PATH')
    
    try:
        # Validate the project name
        if not project_name.replace('-', '').replace('_', '').isalnum():
            return {'success': False, 'message': 'Invalid project name. Use only letters, numbers, hyphens, and underscores.'}

        # Construct the destination path
        destination_root = os.path.abspath(path)
        destination_path = os.path.join(destination_root, project_name)

        # Check if destination already exists
        if os.path.exists(destination_path):
            return {'success': False, 'message': f'Project directory "{destination_path}" already exists.'}

        # Check if parent project exists
        if not os.path.exists(PARENT_PROJECT_PATH):
            return {'success': False, 'message': f'Parent project not found at {PARENT_PROJECT_PATH}'}

        # Ensure base path exists
        os.makedirs(destination_root, exist_ok=True)

        # Copy the entire parent project to the new location
        shutil.copytree(PARENT_PROJECT_PATH, destination_path)

        return {
            'success': True,
            'message': f'Project "{project_name}" successfully created at {destination_path}',
            'project_path': destination_path
        }

    except Exception as e:
        return {'success': False, 'message': f'Error during project creation: {str(e)}'}
    

@mcp.tool('tashkil-install-dependencies')
def tashkil_install_dependencies() -> Dict[str, Any]:
    """
    Install npm packages listed in package.json in the current project directory.
    
    Returns:
        Installation status
    """
    try:
        # Check if package.json exists
        if not os.path.exists('package.json'):
            return {'success': False, 'message': 'No package.json found in current directory'}
        
        # Run npm install
        result = subprocess.run(
            ['npm', 'install'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': 'Dependencies installed successfully',
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'message': 'Failed to install dependencies',
                'error': result.stderr
            }
    
    except Exception as e:
        return {'success': False, 'message': f'Error installing dependencies: {str(e)}'}

@mcp.tool('tashkil-list-dependencies')
def tashkil_list_dependencies() -> Dict[str, Any]:
    """
    List npm packages in the current project
    
    Returns:
        List of dependencies or error message
    """
    try:
        # Check if package.json exists
        if not os.path.exists('package.json'):
            return {'success': False, 'message': 'No package.json found in current directory'}
        
        # Run npm list --depth=0 to get top-level packages
        result = subprocess.run(
            ['npm', 'list', '--depth=0', '--json'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            dependencies = result.stdout
            return {
                'success': True,
                'dependencies': dependencies
            }
        else:
            return {
                'success': False,
                'message': 'Failed to list dependencies',
                'error': result.stderr
            }
    
    except Exception as e:
        return {'success': False, 'message': f'Error listing dependencies: {str(e)}'}
    
@mcp.tool('tashkil-add-dependency')
def tashkil_add_dependency(package: str) -> Dict[str, Any]:
    """
    Add npm packages to the project
    
    Args:
        package: Package name with optional version (e.g., "lodash@latest")
    
    Returns:
        Package installed status
    """
    try:
        # Check if package.json exists
        if not os.path.exists('package.json'):
            return {'success': False, 'message': 'No package.json found in current directory'}
        
        # Run npm install
        result = subprocess.run(
            ['npm', 'install', package],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'Package {package} installed successfully',
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'message': f'Failed to install {package}',
                'error': result.stderr
            }
    
    except Exception as e:
        return {'success': False, 'message': f'Error installing package: {str(e)}'}

@mcp.tool('tashkil-remove-dependency')
def tashkil_remove_dependency(package: str) -> Dict[str, Any]:
    """
    Remove npm packages
    
    Args:
        package: Package name to remove
    
    Returns:
        Package uninstalled status
    """
    try:
        # Check if package.json exists
        if not os.path.exists('package.json'):
            return {'success': False, 'message': 'No package.json found in current directory'}
        
        # Run npm uninstall
        result = subprocess.run(
            ['npm', 'uninstall', package],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'Package {package} removed successfully',
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'message': f'Failed to remove {package}',
                'error': result.stderr
            }
    
    except Exception as e:
        return {'success': False, 'message': f'Error removing package: {str(e)}'}

@mcp.tool('tashkil-welcome')
def tashkil_welcome() -> str:
    """
    Generate a welcome message
    """
    return 'Welcome to Tashkil Coder - Your Full stack Development Assistant!'



if __name__ == '__main__':
    mcp.run()