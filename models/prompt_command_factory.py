from models.prompt_commands import (PromptCommand, MetaDataPromptCommand, ImagePromptCommand, ExamplePromptCommand,
                                    DefaultPromptCommand)

class PromptCommandFactory:
    @staticmethod
    def create_command(prompt_type: str) -> PromptCommand:
        if prompt_type in ["meta title", "meta description"]:
            return MetaDataPromptCommand()
        elif prompt_type.lower().strip() == "image":
            return ImagePromptCommand()
        elif prompt_type.lower().strip() == "example":
            return ExamplePromptCommand()
        else:
            return DefaultPromptCommand()
