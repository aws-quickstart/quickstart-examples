FROM golang:1.9 as builder
RUN go get -d -v golang.org/x/net/html
RUN go get -d -v github.com/alexellis/href-counter/
WORKDIR /go/src/github.com/alexellis/href-counter/.
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/alexellis/href-counter/app .
CMD ["./app"]