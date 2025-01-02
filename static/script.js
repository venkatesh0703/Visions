document
  .getElementById("generateImageBtn")
  .addEventListener("click", function () {
    const prompt = document.getElementById("prompt").value;
    if (!prompt) {
      alert("Please enter a prompt!");
      return;
    }

    // Send request to the Flask API to generate image
    fetch("/generate-image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: prompt }),
    })
      .then((response) => response.json())
      .then((data) => {
        const imagePath = data.image_path;
        document.getElementById(
          "preview"
        ).innerHTML = `<img src="${imagePath}" alt="Generated Image" width="500">`;
        const downloadLink = document.getElementById("downloadLink");
        downloadLink.href = imagePath;
        downloadLink.style.display = "block";
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

document
  .getElementById("generateVideoBtn")
  .addEventListener("click", function () {
    const prompt = document.getElementById("prompt").value;
    if (!prompt) {
      alert("Please enter a prompt!");
      return;
    }

    // Send request to the Flask API to generate video
    fetch("/generate-video", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: prompt }),
    })
      .then((response) => response.json())
      .then((data) => {
        const videoPath = data.video_path;
        document.getElementById(
          "preview"
        ).innerHTML = `<video width="500" controls>
                                                            <source src="${videoPath}" type="video/mp4">
                                                            Your browser does not support the video tag.
                                                          </video>`;
        const downloadLink = document.getElementById("downloadLink");
        downloadLink.href = videoPath;
        downloadLink.style.display = "block";
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
