import os
import sys

class Utils:
    """This class is used for the utility functions"""
    @staticmethod
    def log_error(file:str, message: str, func_name: str = None, **kwargs) -> None:
        """This function handles error detection"""

        try:
            with open(file, "a") as w1:  # open error file
                if func_name:
                    w1.write(f"Error in function {func_name}: \n{message}\n")  # Log function name
                else:
                    w1.write(f"Error: {message}\n")  # Log just the message

                if kwargs:
                    for key, value in kwargs.items():
                        w1.write(f"{key}: \n{value}\n")  # Log additional context
        except Exception as e:
            print(f"Failed to write to error log: {e}")
            
    @staticmethod
    def remove_error_file(file: str) -> None:
        """This is a cleanup function that will remove the error file when no error is detected"""
        
        if os.path.isfile(file): # if the error file exists
            os.remove(file) # remove the error file

    @staticmethod
    def file_issues_checker(error_file: str, file: str, valid_size: int) -> None:
        """This function handles checking for valid file sizes"""
        if not os.path.isfile(file):
            Utils.log_error(error_file, f"The file {file} either does not exist in the {os.getcwd()} directory or was renamed by the user.", func_name='file_issues_checker')
            sys.exit(1)
        elif os.path.getsize(file) != valid_size:
            Utils.log_error(error_file, f"The file {file} has a file size that does not match a valid SAN11RES.BIN file, was it incorrectly modified?", func_name='file_issues_checker')
            sys.exit(1)
            
class ROTK11PS2():
    """This class handles the main logic for applying mods to ROTK11"""
    ROTK11_FILE = "ROTKXI.iso" # the main file that stores all files for ROTK11
    ROTK11_RES_FILE = "SAN11RES.BIN" # the container file that holds scenario files but will be used for mod disabling
    SCENARIO_FILE_OFFSET = 0x699800 # offset for where the SAN11RES.BIN file is within the iso file
    SAN11RES_FILE_SIZE = 467015680 # the correct file size for a SAN11RES.BIN file
    ERROR_LOG_FILE = "ROTK11_Injection_Error.txt" # text file storing possible errors encountered
    def __init__(self) -> None:
        self.user_mod_file = None # used for the user's mod file
        self.user_mod_file_data = None # used for the file data from the user's mod file
        self.util_caller = Utils
        valid_answers = {'apply', 'disable'}
        
        while True:
            self.user_answer = input("Do you want to apply or disable a mod? (apply/disable): ") # ask the user if they want to inject a mod or disable a mod
            if self.user_answer.lower() not in valid_answers:
                print(f"Error: The answer given '{self.user_answer}' was not a valid answer.")
                continue
            if self.user_answer.lower() == 'apply':
                self.file_check_protocol() # call the file checking function
                
            else:
                self.mod_file_disabling(self.ROTK11_FILE, self.ROTK11_RES_FILE)
            break
        
    def file_check_protocol(self) -> None:
        """This class handles checking of the user's mod file and if valid will call the injection function"""
        if len(sys.argv) > 1:
            self.user_mod_file = sys.argv[1]
            self.util_caller.file_issues_checker(self.ERROR_LOG_FILE, self.user_mod_file, self.SAN11RES_FILE_SIZE) # if the user's mod file is smaller or greater than a valid SAN11RES.BIN file
            self.mod_file_injecting(self.ROTK11_FILE, self.user_mod_file) # if valid then call mod injecting function
        else:
            self.util_caller.log_error(self.ERROR_LOG_FILE, "No file was injected, did you drag and drop the mod file or correctly used the command prompt?")
            sys.exit(1)
    def file_handling_protocol(self, main_file: str, injection_file: str) -> None:
        """This function handles the reading and writing logic for mod enabling and disabling"""
        try:
            with open(main_file, "r+b") as f1, open(injection_file, "rb") as f2:
                f1.seek(self.SCENARIO_FILE_OFFSET)
                injection_data = f2.read()
                f1.write(injection_data)
        except FileNotFoundError:
            self.util_caller.log_error(self.ERROR_LOG_FILE, f"The file {main_file} does not exist.", "func_name=file_handling_protocol")
            sys.exit(1)
        except PermissionError:
            self.util_caller.log_error(self.ERROR_LOG_FILE, f"Permission denied for file {main_file}.", "func_name=file_handling_protocol")
            sys.exit(1)
        except IOError as e:
            self.util_caller.log_error(self.ERROR_LOG_FILE, f"An I/O error occurred. Details: {e}", func_name="file_handling_protocol", container=main_file)
            sys.exit(1)
        except Exception as e:
            self.util_caller.log_error(self.ERROR_LOG_FILE, f"Failed to create or write to {main_file}.", func_name="file_handling_protocol", error=str(e))
            sys.exit(1)
        else:
            self.util_caller.remove_error_file(self.ERROR_LOG_FILE)  # Cleanup if successful
            
    def mod_file_injecting(self, main_file: str, mod_file: str) -> None:
        """This function handles the injection of the mod file"""
        self.file_handling_protocol(main_file, mod_file)
            
    def mod_file_disabling(self, main_file: str, disabling_file: str) -> None:
        """This function handles the disabling of mod files"""
        self.util_caller.file_issues_checker(self.ERROR_LOG_FILE, disabling_file, self.SAN11RES_FILE_SIZE) # call a function from the Util class for file size checking
        self.file_handling_protocol(main_file, disabling_file)
            

if __name__ == "__main__":
    ROTK11PS2()
    input("Task finished, you may exit now.")
