function fetchdata(){
    $.ajax({
     url: '/get_progress',
     type: 'GET',
     success: function(data){

        for (i = 0; i < data['downloads'].length; i++) {
            //get download div
            var download = document.getElementById(data['downloads'][i]['_id']);
            
            if ($('#'+ data['downloads'][i]['_id']).length > 0) {
                //update progress bar
                var progress_Style = "width: " + data['downloads'][i]['progress'] + "%;"
                download.getElementsByClassName("progress-bar")[0].setAttribute("style", progress_Style);
                
                download.getElementsByClassName("progress-bar")[0].setAttribute("aria-valuenow", data['downloads'][i]['progress']);

                download.getElementsByClassName("progress-bar")[0].innerHTML = data['downloads'][i]['progress'] + "%";

                //update complete badge
                download.getElementsByClassName("status-badge")[0].innerHTML = data['downloads'][i]['status'];
            }
        }
     },
     complete:function(data){
      setTimeout(fetchdata, 1500); //timeout after each request to server
     }
    });
}

$(document).ready(function(){
    setTimeout(fetchdata, 1500); //timeout from initial page load
});