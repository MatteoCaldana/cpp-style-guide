import re

def generate_table_of_contents(markdown_content):
    # Find all headings in the Markdown content
    headings = re.findall(r'^(#+\s+(.*))$', markdown_content, flags=re.MULTILINE)

    # Generate the table of contents
    toc = "## Table of Contents\n"
    for heading in headings:
        # Calculate indentation level based on the heading level
        level = heading[0].count('#')
        print(level, heading)
        if level > 1 and heading[1] != "Table of Contents":
            indentation = "  " * (level - 1)

            # Create a link-friendly version of the heading
            link_text = re.sub(r'[^\w\s-]', '', heading[1].lower())
            link_text = re.sub(r'\s+', '-', link_text)

            # Add the TOC entry
            toc += f"{indentation}- [{heading[1]}](#{link_text})\n"

    toc = toc.splitlines()
    markdown_content = markdown_content.splitlines()
    markdown_content = "\n".join(markdown_content[0:1]+toc+markdown_content[1:])
    return markdown_content


with open("README.md.notoc", "r") as fp:
    readme = fp.read()

readme = generate_table_of_contents(readme)

with open("README.md", "w") as fp:
    fp.write(readme)