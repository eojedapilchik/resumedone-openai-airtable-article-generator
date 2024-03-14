from models.blog_design_command_factory import BlogDesignCommandFactory
from models.prompt_commands import (FAQTitleCommand, ItwQuestionTemplatePromptCommand, PromptCommand, MetaDataPromptCommand,
                                    ImagePromptCommand,
                                    DefaultPromptCommand, HTMLPromptCommand, InternalReferenceSectionCommand,
                                    SampleCoverLetterCommand, SampleResumeExampleCommand)


class PromptCommandFactory:
    @staticmethod
    def create_command(blog_name:str, prompt_type: str) -> PromptCommand:
        if prompt_type in ["meta title", "meta description"]:
            return MetaDataPromptCommand()
        elif prompt_type.lower().strip() == "image":
            return ImagePromptCommand()
        elif prompt_type in ["internal reference"]:
            return InternalReferenceSectionCommand()
        elif prompt_type in ["h1", "h2", "h3", "div", "p"]:
            return HTMLPromptCommand()
        elif prompt_type in ["sample cover letter"]:
            return SampleCoverLetterCommand()
        elif prompt_type in ["itw question template"]:
            return ItwQuestionTemplatePromptCommand()
        elif prompt_type in ["sample resume example"]:
            return SampleResumeExampleCommand()
        elif prompt_type in ["faq title"]:
            return FAQTitleCommand()
        elif prompt_type.lower().strip() in ["faq content", "example"]:
            return BlogDesignCommandFactory.create_command(blog_name, prompt_type)
        else:
            return DefaultPromptCommand()
