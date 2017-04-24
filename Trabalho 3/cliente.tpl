<!DOCTYPE html>
<html>
<head>

    <title>Chat</title>
</head>

<body>
    <form action="/servidor" method="post">
        Usuário: <input name="username" type="text" />
        Mensagem: <input name="text" type="text" />
        <input value="Send" type="submit" />
    </form>
    <div id = "chat">
        %for (n, m, t) in msg:
            {{n}}: {{m}}<br>
        %end
    </div>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
   <script type="text/javascript">
     var auto_refresh = setInterval(function (){ $("#chat").load("/cliente #chat"); }, 1000);
   </script>
</body>
</html>
