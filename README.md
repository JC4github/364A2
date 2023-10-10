# Chat Application

## Introduction

This project is a simple, secure client-server chat application developed in Python 3.11.5, designed to ensure data confidentiality and user authentication.

## Installation

To get started, follow these steps:

1. **Clone the Repository:**
   Clone this project's repository from [https://github.com/JC4github/364A2](https://github.com/JC4github/364A2) to your local machine.

2. **Navigate to the Project Directory:**
   Open your terminal or console and navigate to the project directory using the `cd` command.

## Usage

**Note**: Depending on your specific version and configuration of Python, you may need to run the program using either of the following commands:

```bash
python
```

or

```bash
py
```

instead of `python3`.

### Running the Server

1. Start the server by running the following command:
   ```bash
   python3 chat_server.py --name=server --port=9988
   ```



### Running Client Instances

2. In separate terminal/console windows, create client instances using this command:
   ```bash
   python3 chat_client.py --port=9988
   ```

3. You can create additional client instances by repeating step 2.

## Important Note

Please ensure that you are using Python 3.11.5 or a compatible version. Running the application on a different Python version may result in compatibility issues. This application is also developed on Mac OS, running this application on windows or other operating systems may result in different terminal bahaviour, it is best to use the terminal from Mac OS if possible. 
