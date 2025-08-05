# <img src="https://i.imgur.com/Og6gFnB.png" alt="Fivetran Logo" width="100" style="vertical-align: middle;"/> Fivetran | Snowflake HOL 2025

# 💻 Fivetran Hands-on Lab Pre-Requisites: Laptop Requirements

We are going to have a great lab demonstrating the ease at which Fivetran allows you to add your custom data sources to your Snowflake destination. You should have received an email post lab registration that provides the requirements for your development environment. The below items must be done prior to us starting the lab as our instructors and Q&A folks will only be able to answer questions pertaining to Fivetran, Snowflake, and Fivetran Connector SDK. Because of the wide range of development options, we will not be assisting in setting up your environment or answering environment setup-related questions.

-----

## Python Environment 🐍

You will need to have **Python version 3.9, 3.10, 3.11, or 3.12** installed and verified on your system. The instructor will be using **Python 3.12.8**.

While detailed installation instructions are beyond the scope of this document, here are some common approaches for managing Python versions:

  * **Multiple Python Versions:** For managing multiple Python versions (e.g., if you have other projects requiring different versions), consider tools like `pyenv` for macOS or the **Python Launcher** for Windows.
  * **Universal Installer:** You can always download a universal installer for your desired Python version directly from [python.org](https://www.python.org/).

**Verification:** To verify your Python installation, open your terminal or command prompt and enter:

```bash
python3 --version
```

You should see an output indicating your installed Python version (e.g., `Python 3.12.8`).

**Virtual Environments:** You will also need to understand how to create, activate, and deactivate Python virtual environments, which are crucial for managing project dependencies.

-----

## Integrated Development Environment (IDE) 📝

You'll need an IDE or code editor to develop your Fivetran Connector. Here are some popular options:

  * **[Visual Studio Code (free)](https://code.visualstudio.com/download)** (highly recommended)
  * **[PyCharm Community Edition (free)](https://www.jetbrains.com/pycharm/download/other.html)**
  * **[Cursor Hobby Plan (limited free)](https://cursor.com/pricing)**
  * A simple text editor (e.g., Mac TextEdit, Windows Notepad)

-----

## Database Query Tool 📊

A database query tool capable of opening a **DuckDB file** is required. A recommended option is:

  * **[DBeaver](https://dbeaver.io/download/)** - Note that the first time you try to open a DuckDB file, you will be prompted to download the plugin. Another side note, is if you do intend to use DBeaver, choose the **New Database Connection** option and choose **DuckDB** from the list versus the "open file" method.  DBeaver will save your connection; so once the new connection is established, the reference will not go away upon closing DBeaver.

-----

## Access to a Large Language Model (LLM) 🧠

### 🔥🔥🔥 ATTENDEES WILL NOT BE CODING THIS BY HAND/MANUALLY (YAY)\! 🔥🔥🔥

You **must** have access to a Large Language Model to assist with the coding tasks during the lab. These models will significantly streamline the development process. (And don't worry about learning how to prompt for the best code output. We will have some basic prompts ready to go the day of the lab.) Recommended LLMs include:

  * **Google Gemini** (instructor tested)
  * **Anthropic Claude** (instructor tested)
  * **Open AI ChatGPT** (instructor tested)
  * **Meta.ai Llama** (instructor tested)
  * **DeepSeek** (instructor tested)
-----

## Folder Structure for Code 📁

  * Create a folder for the lab code.
  * Ensure the code folder does NOT have spaces in the path (coding best practice).
  * Ensure the code folder does NOT reside under a system folder such as "My Documents" for Windows or "Documents" for macOS.
-----

# Fivetran and Snowflake Lab Accounts

No need to start trials for Fivetran or Snowflake. We have already provisioned these accounts for you.  We will walk through these login processes on lab day. 

## Fivetran

1. You will receive an email on the day of the lab with the subject line **David Hrncir Invited You to Join Fivetran!** for the email used during registration.  Note that if you do not see this email, you may need to check your junk/spam folder.
2. Click the **Accept Invite** link in the email and follow the instructions. Remember to keep your password handy.
3. If you close your browser tab for the Fivetran UI, no worries. Simply launch a new tab and go to the **[Fivetran Login Page](https://fivetran.com/login)** to re-login.
4. The account name shown in the upper left corner of the screen will be **MDS_SNOWFLAKE_HOL**.

<div style="background-color: #fff3cd; padding: 12px 16px; border-left: 6px solid #ffcc00; margin-bottom: 20px; margin-top: 10px;">
  <strong>⚠️ NOTE:</strong><br>
If you are a current Fivetran customer, you will notice that you will be taken right into the Fivetran UI as you normally would and defaulted to your company's account. Simply click your company's account name in the upper left corner of the Fivetran UI to switch accounts to the <strong>MDS_SNOWFLAKE_HOL</strong> account.
</div>

## Snowflake

1. On the day of the lab, the instructor will provide you with your password to the **[Fivetran provisioned Snowflake account](https://aa67604.us-central1.gcp.snowflakecomputing.com/console/login#/)**.
2. Your Snowflake user login Id will be in the following format:  **HOL_[first name]_[last_name]_USER**
3. The password will be provided in the chat on lab day and will only be valid during lab time.
-----

# Let's build a custom connector!

There are 9 verticals available from which to choose in this git repo. Click on the vertical you would like to work with today, and we will walk through the folder structure.  Note that each vertical is set up in the same manner. So no matter which vertical you choose, you will be able to follow along.

## Let's go!
