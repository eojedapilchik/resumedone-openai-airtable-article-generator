from models.prompt_commands import (ExampleDefaultPromptCommand, CommonFAQContentCommand, FAQDefaultContentCommand, FAQTitleCommand, PromptCommand, MetaDataPromptCommand, ImagePromptCommand, CommonExamplePromptCommand,
                                    DefaultPromptCommand, HTMLPromptCommand, InternalReferenceSectionCommand,
                                    SampleCoverLetterCommand, SampleResumeExampleCommand)


class BlogDesignCommandFactory:
    @staticmethod
    def create_command(blog_name: str, prompt_type:str) -> PromptCommand:
        if prompt_type.lower().strip() == "example":
            if blog_name:
                if blog_name.strip() in ['kreatorcv.com']:
                    return ExampleDefaultPromptCommand()
                else:
                    return CommonExamplePromptCommand()
            else:
                return ExampleDefaultPromptCommand()
        elif prompt_type in ["faq content"]:
            if blog_name:
                if blog_name.strip() in ['kreatorcv.com']:
                    return FAQDefaultContentCommand()
                else:
                    return CommonFAQContentCommand()
            else:
                return FAQDefaultContentCommand()
        else:
            return DefaultPromptCommand()
