function getLeadingHtml (input, maxChars) {
	// token matches a word, tag, or special character
	var	token = /\w+|[^\w<]|<(\/)?(\w+)[^>]*(\/)?>|</g,
		selfClosingTag = /^(?:[hb]r|img)$/i,
		output = "",
		charCount = 0,
		openTags = [],
		match;

	// Set the default for the max number of characters
	// (only counts characters outside of HTML tags)
	maxChars = maxChars || 250;

	while ((charCount < maxChars) && (match = token.exec(input))) {
		// If this is an HTML tag
		if (match[2]) {
			output += match[0];
			// If this is not a self-closing tag
			if (!(match[3] || selfClosingTag.test(match[2]))) {
				// If this is a closing tag
				if (match[1]) openTags.pop();
				else openTags.push(match[2]);
			}
		} else {
			charCount += match[0].length;
			if (charCount <= maxChars) output += match[0];
		}
	}

	// Close any tags which were left open
	var i = openTags.length;
	while (i--) output += "</" + openTags[i] + ">";
	
	return output;
};
function collapse(id) {
  el=document.getElementById(id);
  el.innerHTML = el.newhtml;
}
function expand(id) {
  el=document.getElementById(id);
  el.innerHTML = el.oldhtml;
}
function excerpt(id) {
  el=document.getElementById(id);
  expanded=el.innerHTML;
  collapsed=cutHtmlString(el.innerHTML,500);
  if(expanded != collapsed) {
      el.oldhtml= expanded+ "<a href=\"javascript:collapse('" + id + "')\">(collapse)</a>";
      el.newhtml=collapsed+"<a href=\"javascript:expand('" + id + "')\">(more...)</a>";
      collapse(id);
  }
}
