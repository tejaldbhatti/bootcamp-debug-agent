from query import diagnose

result = diagnose(
    "I'm getting this error, see the screenshot",
    image_path=r"C:\Users\Denish\Desktop\TA\AC_bootcamp\Week_5\project\bootcamp-debug-agent\bootcamp-debug-agent\screenshot.png"  # use any real error screenshot you have saved
)
print(result["answer"])