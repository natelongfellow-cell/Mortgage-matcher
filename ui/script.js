async function compare() {
  const f1 = document.getElementById("file1").files[0];
  const f2 = document.getElementById("file2").files[0];

  if (!f1 || !f2) {
    alert("Please select both files.");
    return;
  }

  const form = new FormData();
  form.append("file1", f1);
  form.append("file2", f2);

  const res = await fetch("/compare", {
    method: "POST",
    body: form
  });

  const data = await res.json();
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
}
