###Create a virtual environment

- Create a virtual environment by running the following command
  
  On Windows :

        python -m venv env

  On Linux/macOS

        python3 -m venv env

- Activate the virtual environment. Run the below at the prompt from the folder where you created the virtual environment

        ./env/Scripts/activate

- Once successfully activated the terminal prompt changes to

        (env) PS C:\Users\myName\Documents\GitHub\project>

- Install requirements

        pip3 install -r requirements.txt       


        pip3 freeze > requirements.txt
