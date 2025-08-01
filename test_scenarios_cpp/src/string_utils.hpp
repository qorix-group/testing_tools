#pragma once

#include <string>
#include <vector>

namespace string_utils {

/// @brief Split string by the delimiter.
/// @param str Input string.
/// @param delimiter Delimiter.
/// @return List of string parts. E.g., ("1;2;3", ";") -> ["1", "2", "3"].
std::vector<std::string> split(const std::string& str, const std::string& delimiter);

/// @brief Join string by the delimiter.
/// @param parts Input string parts.
/// @param delimiter Delimiter.
/// @return Joined string. E.g., (["1", "2", "3"], ";") -> "1;2;3".
std::string join(const std::vector<std::string>& parts, const std::string& delimiter);

/// @brief Trim surrounding whitespace.
/// @param str Input string.
/// @return Trimmed string. E.g., "   123   " -> "123".
std::string trim(const std::string& str);

}  // namespace string_utils
