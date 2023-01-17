#ifndef Logger_included
#define Logger_included

#include <string>
#define LOGGING __FILE__, __LINE__
namespace Logger
{
	void Log( const std::string& f, int n, const std::string& str );
    void Log( const std::string& f, int n, const std::wstring& str );
};

#endif
