#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sqlite3.h>
#include <string>

namespace py = pybind11;

bool insert_translation(const std::string& db_path,
                        const std::string& source_text,
                        const std::string& target_text,
                        const std::string& lang_pair) {
    sqlite3* db;
    sqlite3_stmt* stmt;
    std::string sql = "INSERT OR IGNORE INTO translations (source_text, target_text, lang_pair) VALUES (?, ?, ?);";

    if (sqlite3_open(db_path.c_str(), &db) != SQLITE_OK) {
        return false;
    }

    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
        sqlite3_close(db);
        return false;
    }

    sqlite3_bind_text(stmt, 1, source_text.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, target_text.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, lang_pair.c_str(), -1, SQLITE_STATIC);

    bool success = (sqlite3_step(stmt) == SQLITE_DONE);

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    return success;
}

PYBIND11_MODULE(cache_writer, m) {
    m.def("insert_translation", &insert_translation, "Insert translation into SQLite cache");
}