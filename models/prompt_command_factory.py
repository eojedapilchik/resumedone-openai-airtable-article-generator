from models.prompt_commands import (PromptCommand, MetaDataPromptCommand, ImagePromptCommand, ExamplePromptCommand,
                                    DefaultPromptCommand, HTMLPromptCommand)

class PromptCommandFactory:
    @staticmethod
    def create_command(prompt_type: str) -> PromptCommand:
        if prompt_type in ["meta title", "meta description"]:
            return MetaDataPromptCommand()
        elif prompt_type.lower().strip() == "image":
            return ImagePromptCommand()
        elif prompt_type.lower().strip() == "example":
            return ExamplePromptCommand()
        elif prompt_type in ["h1", "h2", "h3", "div", "p"]:
            return HTMLPromptCommand()
        else:
            return DefaultPromptCommand()
