$(document).ready(function() {

    $(document).on('click', '#start_download', function() {
        var download_link = $('#download_link').val();
        
        req = $.ajax({
            url : '/start_download',
            type : 'POST',
            data : { download_link : download_link }
        });
        
        req.done(function(data) {
            if (data['success'] == true){
                
                //add download details to the downloads container
                $("#downloads_container").append(`
                    <div class="download_container mt-3 mb-1" id="`+data['download_data']['_id']+`">
                        <div class="card">
                            <img src="`+ data['download_data']['image_url'] +`" style="max-width: 12%; height: auto;" class="card-img-top" draggable="false">
                            <div class="card-body">
                                <a href="javascript:void(0)" class="float-right" id="delete_download" download_id="`+ data['download_data']['_id'] +`"><i class='fa fa-trash' style='color: red'></i></a>
                                <h5 class="card-title">`+ data['download_data']['title'] +`</h5>
                                <p class="card-text">
                                    <span class="badge badge-secondary">`+ data['download_data']['website_name'] +`</span> <span class="badge badge-secondary">`+ data['download_data']['chapters'] +` Chapters</span> <span class="badge badge-secondary status-badge">`+ data['download_data']['status'] +`</span>
                                </p>
                                <div class="progress" style="margin-top: 5em;">
                                    <div class="progress-bar" role="progressbar" style="width: `+data['download_data']['progress']+`%;" aria-valuenow="`+data['download_data']['progress']+`" aria-valuemin="0" aria-valuemax="100">`+data['download_data']['progress']+`%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `)

                $("#download_link").val('')
                
            }
            else{
                console.log("Error starting download!");
            }

        });

    });

    $(document).on('click', '#delete_download', function() {
        var download_id = $(this).attr('download_id');
        
        req = $.ajax({
            url : '/delete_download',
            type : 'POST',
            data : { download_id : download_id }
        });
        
        req.done(function(data) {
            if (data['success'] == true){
                
                //remove html
                $("#"+download_id).remove()
                
            }
            else{
                console.log("Error deleting download!");
            }

        });

    });

});