
//////// FAQs pop up window //////////

var policyContent = `
Cancellation and Refund Policy

In the event of cancellation, refunds will be provided based on the following schedule:

Cancellation 30 or more days prior to the event: 100% refund
Cancellation 15-29 days prior to the event: 50% refund
Cancellation within 14 days of the event: No refund

`;

// Get the "FAQs" link element by its ID
var faqLink = document.getElementById("faqLink");

// Add a click event listener to the "FAQs" link
faqLink.addEventListener("click", function(event) {
  // Prevent the default link behavior (navigating to a new page)
  event.preventDefault();
  
  // Display the policy content in a pop-up window using the alert function
  alert(policyContent);
});
