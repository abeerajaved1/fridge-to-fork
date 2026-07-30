const form = document.getElementById("order-form");
const sendBtn = document.getElementById("send-btn");
const errorMsg = document.getElementById("error-msg");
const printer = document.getElementById("printer");
const receiptWrap = document.getElementById("receipt-wrap");
const receipt = document.getElementById("receipt");
const againBtn = document.getElementById("again-btn");
const ingredientsInput = document.getElementById("ingredients");
const preferenceInput = document.getElementById("preference");

function setLoading(isLoading) {
  sendBtn.disabled = isLoading;
  sendBtn.textContent = isLoading ? "Cooking…" : "Send to kitchen →";
  printer.hidden = !isLoading;
}

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.hidden = false;
}

function clearError() {
  errorMsg.hidden = true;
  errorMsg.textContent = "";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderRecipe(recipe) {
  const ingredientItems = (recipe.ingredients || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const stepItems = (recipe.steps || [])
    .map((step) => `<li>${escapeHtml(step)}</li>`)
    .join("");

  const notesHtml = recipe.notes
    ? `<p class="notes">Note: ${escapeHtml(recipe.notes)}</p>`
    : "";

  const servingsHtml = recipe.servings
    ? `<p class="servings">${escapeHtml(recipe.servings)}</p>`
    : "";

  receipt.innerHTML = `
    <div class="stamp">${recipe.emoji || "🍽️"}</div>
    <h2>${escapeHtml(recipe.name || "Recipe")}</h2>
    ${servingsHtml}
    <h3>Ingredients</h3>
    <ul>${ingredientItems}</ul>
    <h3>Steps</h3>
    <ol>${stepItems}</ol>
    ${notesHtml}
  `;

  receiptWrap.hidden = false;
}

async function requestRecipe(ingredients, preference) {
  clearError();
  receiptWrap.hidden = true;
  setLoading(true);

  try {
    const res = await fetch("/api/recipe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ingredients, preference }),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    renderRecipe(data.recipe);
  } catch (err) {
    showError("Couldn't reach the kitchen. Check your connection and try again.");
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const ingredients = ingredientsInput.value.trim();
  const preference = preferenceInput.value.trim();

  if (!ingredients) {
    showError("The pad is blank — write down at least one ingredient.");
    return;
  }

  requestRecipe(ingredients, preference);
});

// Bonus: ask for another recipe without restarting / reloading the page.
againBtn.addEventListener("click", () => {
  receiptWrap.hidden = true;
  ingredientsInput.value = "";
  ingredientsInput.focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
