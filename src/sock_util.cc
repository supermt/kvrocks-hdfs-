#include <unistd.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <event2/util.h>
#include <glog/logging.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <poll.h>
#include <errno.h>
#include <string>

#include "sock_util.h"

#ifndef POLLIN
# define POLLIN      0x0001    /* There is data to read */
# define POLLPRI     0x0002    /* There is urgent data to read */
# define POLLOUT     0x0004    /* Writing now will not block */
# define POLLERR     0x0008    /* Error condition */
# define POLLHUP     0x0010    /* Hung up */
# define POLLNVAL    0x0020    /* Invalid request: fd not open */
#endif

sockaddr_in new_sockaddr_inet(const std::string &host, uint32_t port) {
  sockaddr_in sin{};
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = inet_addr(host.c_str());
  sin.sin_port = htons(port);
  return sin;
}

int sock_check_liveness(int fd) {
  struct pollfd rfd[1];
  rfd[0].fd = fd;
  rfd[0].events = POLLIN|POLLPRI|POLLERR|POLLHUP;
  rfd[0].revents = 0;

  if (poll(rfd, 1, 0) > 0) {
    char buf[1];
    ssize_t n = recv(fd, buf, sizeof(buf), MSG_PEEK);
    if (n == 0 || (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK)) {
      return 0;
    }
  }
  return 1;
}

int sock_connect(std::string host, uint32_t port, int* fd) {
  sockaddr_in sin{};
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = inet_addr(host.c_str());
  sin.sin_port = htons(port);
  *fd = socket(AF_INET, SOCK_STREAM, 0);
  auto rv = connect(*fd, (sockaddr*)&sin, sizeof(sin));
  if (rv < 0) {
    LOG(ERROR) << "[Socket] Failed to connect: "
               << evutil_socket_error_to_string(EVUTIL_SOCKET_ERROR());
    return rv;
  }
  setsockopt(*fd, SOL_SOCKET, SO_KEEPALIVE, nullptr, 0);
  setsockopt(*fd, IPPROTO_TCP, TCP_NODELAY, nullptr, 0);
  return 0;
}

int sock_send(int fd, const std::string &data) {
  auto rv = send(fd, data.c_str(), data.length(), 0);
  if (rv < 0) {
    LOG(ERROR) << "[Socket] Failed to send: "
               << evutil_socket_error_to_string(EVUTIL_SOCKET_ERROR());
    return -1;
  }
  return 0;
}

int get_peer_addr(int fd, std::string *addr, uint32_t *port) {
  sockaddr_storage sa{};
  socklen_t sa_len = sizeof(sa);
  if (getpeername(fd, reinterpret_cast<sockaddr *>(&sa), &sa_len) < 0) {
    return -1;
  }
  if (sa.ss_family == AF_INET) {
    auto sa4 = reinterpret_cast<sockaddr_in*>(&sa);
    char buf[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, reinterpret_cast<void*>(&sa4->sin_addr), buf, INET_ADDRSTRLEN);
    addr->clear();
    addr->append(buf);
    *port = sa4->sin_port;
    return 0;
  }
  return -2; // only support AF_INET currently
}
