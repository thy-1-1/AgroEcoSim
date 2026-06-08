const scenarios = {
  baseline: {
    label: "Reference system",
    title: "Conventional baseline",
    description: "Seasonal chemical intervention establishes the reference level for productivity and ecological pressure.",
    stability: "0.5299",
    chemical: "High",
    output: "Reference"
  },
  withdrawal: {
    label: "Chemical reduction",
    title: "Chemical withdrawal",
    description: "Chemical mortality terms are removed to examine the short-term yield and long-term stability trade-off.",
    stability: "Improved",
    chemical: "None",
    output: "Lower peak"
  },
  bats: {
    label: "Biological control",
    title: "Bat-assisted control",
    description: "Predation and pollination effects are added to test a multifunctional biological intervention.",
    stability: "-11.542 lambda",
    chemical: "Reduced",
    output: "Higher"
  },
  bees: {
    label: "Pollination support",
    title: "Bee-assisted pollination",
    description: "Pollination support is isolated from strong predation effects to compare alternative species introductions.",
    stability: "-9.567 lambda",
    chemical: "Reduced",
    output: "Higher"
  },
  integrated: {
    label: "Mixed intervention",
    title: "Integrated biocontrol",
    description: "Reduced chemical inputs are combined with predators and pollinators to test a balanced intervention strategy.",
    stability: "High",
    chemical: "Low",
    output: "Resilient"
  },
  organic: {
    label: "Transition pathway",
    title: "Organic agriculture",
    description: "Chemical pressure is phased out while soil regeneration and biological control improve long-term system response.",
    stability: "0.7141",
    chemical: "Minimal",
    output: "Long-term gain"
  }
};

const buttons = document.querySelectorAll("[data-scenario]");
const label = document.querySelector("#scenario-label");
const title = document.querySelector("#scenario-title");
const description = document.querySelector("#scenario-description");
const stability = document.querySelector("#scenario-stability");
const chemical = document.querySelector("#scenario-chemical");
const output = document.querySelector("#scenario-output");

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    buttons.forEach((candidate) => candidate.classList.remove("active"));
    button.classList.add("active");
    const scenario = scenarios[button.dataset.scenario];
    label.textContent = scenario.label;
    title.textContent = scenario.title;
    description.textContent = scenario.description;
    stability.textContent = scenario.stability;
    chemical.textContent = scenario.chemical;
    output.textContent = scenario.output;
  });
});
