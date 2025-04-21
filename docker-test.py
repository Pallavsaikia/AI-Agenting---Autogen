from pathlib import Path

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
import asyncio
work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)

async def main():
    async with DockerCommandLineCodeExecutor(work_dir=work_dir) as executor:  # type: ignore
        a=await executor.execute_code_blocks(
                code_blocks=[
                    CodeBlock(language="python", code="print('Hello, World!')"),
                ],
                cancellation_token=CancellationToken(),
            )
        print(a.output)
        
# Run the async app
asyncio.run(main())
