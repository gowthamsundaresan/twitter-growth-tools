#include <node.h>
#include <v8.h>
#include <unistd.h>

using namespace v8;

Handle<Value> MyUSleep(const Arguments& args) {
  HandleScope scope;
  uint32_t val = args[0]->Uint32Value();
  usleep(val);
  return scope.Close(Undefined());
}

void init(Handle<Object> target) {
  NODE_SET_METHOD(target, "usleep", MyUSleep);
}

NODE_MODULE(sleep, init);
