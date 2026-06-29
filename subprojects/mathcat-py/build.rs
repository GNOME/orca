use std::path::PathBuf;
use zip::ZipArchive;

fn main() {
    let archive = libmathcat::shim_filesystem::ZIPPED_RULE_FILES;
    let archive = std::io::Cursor::new(archive);
    let location = PathBuf::from("addon/globalPlugins/MathCAT");

    let mut zip_archive = ZipArchive::new(archive).unwrap();
    zip_archive.extract(&location).expect("Zip extraction failed");

    // Extract nested per-language and per-braille-code zip files so that
    // the installed Rules directory doesn't need write access at runtime.
    let rules_dir = location.join("Rules");
    extract_nested_zips(&rules_dir);
}

fn extract_nested_zips(dir: &PathBuf) {
    let entries: Vec<_> = match std::fs::read_dir(dir) {
        Ok(entries) => entries.filter_map(|e| e.ok()).collect(),
        Err(_) => return,
    };

    for entry in entries {
        let path = entry.path();
        if path.is_dir() {
            extract_nested_zips(&path);
        } else if path.extension().map_or(false, |ext| ext == "zip") {
            if let Ok(data) = std::fs::read(&path) {
                let cursor = std::io::Cursor::new(data);
                if let Ok(mut archive) = ZipArchive::new(cursor) {
                    let parent = path.parent().unwrap();
                    let _ = archive.extract(parent);
                    let _ = std::fs::remove_file(&path);
                }
            }
        }
    }
}
