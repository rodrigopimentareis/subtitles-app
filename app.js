var express = require('express');
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var path = require('path');
var formidable = require('formidable');
var fs = require('fs');
var cfenv = require('cfenv');


app.use(express.static(path.join(__dirname, 'public')));


app.get('/', function(req, res){
  res.sendfile('views/index.html');
});

app.post('/upload', function(req, res){

  // create an incoming form object
  var form = new formidable.IncomingForm();
  var file_name = '';
  // specify that we want to allow the user to upload multiple files in a single request
  form.multiples = true;

  // store all uploads in the /uploads directory
  form.uploadDir = path.join(__dirname, '/uploads');

  // every time a file has been uploaded successfully,
  // rename it to it's orignal name
  form.on('file', function(field, file) {
    file_name = path.join(form.uploadDir, file.name)
    fs.rename(file.path, file_name);   
  });

  // log any errors that occur
  form.on('error', function(err) {
    console.log('An error has occured: \n' + err);
  });

  // once all the files have been uploaded, send a response to the client
  form.on('end', function() {
    const execFile = require('child_process').execFile;
    io.emit('news', { status: 'begin' });

    const child = execFile('python',['generate_subtitle.py',file_name], (error, stdout, stderr) => {
      if (error) {
        console.log('error file:'+file_name);

        throw error;
      }
      console.log(stdout);
    });
    console.log('finished file:'+file_name);
    child.stdout.pipe(process.stdout)
    child.on('exit', function() {
      //result_file = file_name.replace(".mp4", ".txt")
      //fs.readFile(result_file, 'utf8', function (err,data) {
      //  if (err) {
      //    return console.log(err);
      //  }
      //  console.log(data);
          io.emit('news', { status: 'end' });
          //);
      //});
    



      console.log('End processing.');
      
      res.end('success');
      
    })
    
    
  });

  // parse the incoming request containing the form data
  form.parse(req);

});


io.on('connection', function(socket){

  console.log('a user connected');
});

var appEnv = cfenv.getAppEnv();

http.listen(appEnv.port, '0.0.0.0', function(){
  console.log("server starting on " + appEnv.url);
});