// test.c

// COMP 3010
// INSTRUCTOR: Robert Guderian
// NAME: Denys Popov
// ASSIGNMENT: 2

// PURPOSE: test for web_server.py. Tests the post and get methods of the server

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <assert.h>

#include <netdb.h> // For getaddrinfo
#include <unistd.h> // for close
#include <stdlib.h> // for exit
int main(int argc, char **argv)
{
    char * cookie;
    char * tweet;

    if(argc != 3){
        printf("Usage: %s <cookie for the log in> <text of the tweet>\n", argv[0]);
        return 1;
    }

    else
    {
        cookie = malloc(strlen(argv[1])+1);
        tweet = malloc(strlen(argv[2])+1);

        strcpy(cookie, argv[1]);
        strcpy(tweet, argv[2]);
    }


    int socket_desc;
    struct sockaddr_in server_addr;
    char server_message[10000], client_message[10000];
    char address[100];

    struct addrinfo *result;

    // ########################################################################################################
    // ###################### post a tweet test and check that 200 OK was returend ############################
    // ########################################################################################################
    
    // Clean buffers:
    memset(server_message,'\0',sizeof(server_message));
    memset(client_message,'\0',sizeof(client_message));
    
    // Create socket:
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    
    if(socket_desc < 0){
        printf("Unable to create socket\n");
        return -1;
    }
    
    printf("Socket created successfully\n");

    struct addrinfo hints;
    memset (&hints, 0, sizeof (hints));
    hints.ai_family = PF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags |= AI_CANONNAME;
    
    // get the ip of the page we want to scrape
    int out = getaddrinfo ("127.0.0.1", NULL, &hints, &result); //TODO change to the ip of the server
    // fail gracefully
    if (out != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(out));
        exit(EXIT_FAILURE);
    }

    // Set port and IP the same as server-side:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    
     // converts to octets
    printf("Convert...\n");
    inet_ntop (server_addr.sin_family, &server_addr.sin_addr, address, 100);
    printf("Connecting to %s\n", address);
    // Send connection request to server:
    if(connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    printf("Connected with server successfully\n");
    
    //change host to the ip address of the server
    char request[1024];
    char body[1024];
    snprintf(request, 1024, "POST /api/tweet HTTP/1.1\r\nHost: 127.0.0.1\r\nCookie:verySecureCookie=%s\r\n\r\n", cookie);
    snprintf(body, 1024, "{\"tweet\":\"%s\"}", tweet);

    strcat(request, body);
    
    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if(send(socket_desc, request, strlen(request), 0) < 0){
        printf("Unable to send message\n");
        return -1;
    }
    
    // Receive the server's response:
    if(recv(socket_desc, server_message, sizeof(server_message), 0) < 0){
        printf("Error while receiving server's msg\n");
        return -1;
    }
    
    printf("Server's response: %s\n",server_message);
    // assert that the server returned 200 OK
    assert(strcmp(server_message, "HTTP/1.1 200 OK\n\n") == 0);

    // Close the socket:
    close(socket_desc);

    // #####################################################################################################################
    // ###################### get tweets page and assert that the newly created tweet is there  ############################
    // #####################################################################################################################
    // Clean buffers:
    memset(server_message,'\0',sizeof(server_message));
    memset(client_message,'\0',sizeof(client_message));

     // Create socket:
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);

     // converts to octets
    printf("Convert...\n");
    inet_ntop (server_addr.sin_family, &server_addr.sin_addr, address, 100);
    printf("Connecting to %s\n", address);
    // Send connection request to server:
    if(connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    printf("Connected with server successfully\n");

    snprintf(request, 1024, "GET /api/tweet HTTP/1.1\r\nHost: 127.0.0.1\r\nCookie:verySecureCookie=%s\r\n\r\n", cookie);
    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if(send(socket_desc, request, strlen(request), 0) < 0){
        printf("Unable to send message\n");
        return -1;
    }
    
    // Receive the server's response:
    if(recv(socket_desc, server_message, sizeof(server_message), 0) < 0){
        printf("Error while receiving server's msg\n");
        return -1;
    }
    
    printf("Server's response: %s\n",server_message);
    // assert that the server returned 200 OK
    assert(strstr(server_message, "HTTP/1.1 200 OK") != NULL);
    // assert that the tweet is in the response
    assert(strstr(server_message, tweet) != NULL);

    return 0;
}
