
FormatArticles()

function FormatArticles() {
    var responses = document.getElementsByClassName('response');

    for (var i=0; i<responses.length; i++) {
        var responseHTML = responses[i].innerHTML;
        // Loop through every link
        var start_each = 0;
        while (responseHTML.indexOf('(https', start_each) != -1) {
            var link_start = responseHTML.indexOf('(https', start_each)
            var link_end = responseHTML.indexOf(')', link_start)
            var link = responseHTML.substring(link_start+1, link_end)

            var hyperlink_str = "(";
            // Check if there is more than one source
            if ( link.indexOf(',') != -1 ) {
                var links = link.split(', ');

                for ( var j=0; j<links.length; j++ ) {
                    hyperlink_str += "<a href=\"" + links[j] + "\">Source" + (j+1).toString() + "</a>"
                    if ( j != links.length-1 ) {
                        hyperlink_str += ", "
                    }
                }
            }
            else {
                hyperlink_str += "<a href=\"" + link + "\">Source</a>"
            }
            hyperlink_str += ")"

            responseHTML = responseHTML.substring(0, link_start) + hyperlink_str + responseHTML.substring(link_end+1);
        
            responses[i].innerHTML = responseHTML;

            start_each = link_end+1;
        }
    }
}