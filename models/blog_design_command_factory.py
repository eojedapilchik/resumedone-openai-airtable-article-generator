from models.prompt_commands import (ExampleDefaultPromptCommand, CommonFAQContentCommand, FAQDefaultContentCommand, FAQTitleCommand, PromptCommand, MetaDataPromptCommand, ImagePromptCommand, CommonExamplePromptCommand,
                                    DefaultPromptCommand, HTMLPromptCommand, InternalReferenceSectionCommand,
                                    SampleCoverLetterCommand, SampleResumeExampleCommand)


class BlogDesignCommandFactory:
    EXAMPLE_PROMPT = "example"
    FAQ_CONTENT = "faq content"
    SPECIAL_BLOG_NAME = ["kreatorcv.com"]
    
    @staticmethod
    def create_command(blog_name: str, prompt_type:str) -> PromptCommand:
        normalized_prompt_type = prompt_type.lower().strip()
        is_special_blog = blog_name.strip() in BlogDesignCommandFactory.SPECIAL_BLOG_NAME if blog_name else True

        if normalized_prompt_type == BlogDesignCommandFactory.EXAMPLE_PROMPT:
            if is_special_blog:
                return ExampleDefaultPromptCommand()
            return CommonExamplePromptCommand()
        elif normalized_prompt_type == BlogDesignCommandFactory.FAQ_CONTENT:
            if is_special_blog:
                return FAQDefaultContentCommand()
            return CommonFAQContentCommand()
        
        return DefaultPromptCommand()
