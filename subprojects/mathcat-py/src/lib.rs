//! When calling from python, the general ordering is:
//! 1. whatever preferences the AT needs to set, it is done with calls to [`SetPreference`].
//! 2. the MathML is sent over via [`SetMathML`].
//! 3. AT calls to get the speech [`GetSpokenText`] and calls [`GetBraille`] to get the (Unicode) braille.
//!
//! Navigation can be done via calls to either:
//! * [`DoNavigateKeyPress`] (takes key events as input)
//! * [`DoNavigateCommand`] (takes the commands the key events internally map to)
//! Both return a string to speak.
//! To highlight the node on is on, 'id's are used. If they weren't already present,
//! [`SetMathML`] returns a string representing MathML that contains 'id's for any node that doesn't already
//! have an 'id' set. You can get the current node with
//! * [`GetNavigationMathMLId`]
//! * [`GetNavigationMathML`] -- returns a string representing the MathML for the selected node
//! Note: a second integer is returned. This is the offset in characters for a leaf node.
//!   This is needed when navigating by character for multi-symbol leaf nodes such as "sin" and "1234"
//!
//! It is also possible to find out what preferences are currently set by calling [`GetPreference`]
//!
//! AT can pass key strokes to allow a user to navigate the MathML by calling [`DoNavigateKeyPress`]; the speech is returned.
//! To get the MathML associated with the current navigation node, call [`GetNavigationMathML`].
//!

// for Python interfaces --#[...] doesn't help on name mangled python function names
#![allow(non_snake_case)]
#![allow(clippy::needless_return)]

use libmathcat::*;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::exceptions::PyOSError;

/// The error type returned from MathCAT is from an error package, so we can't implement From on it.
/// Instead, we write a wrapper function that deals with the error conversion
fn convert_error<T>(result: Result<T, libmathcat::errors::Error>) -> PyResult<T> {
    return match result {
        Ok(answer) => Ok(answer),
        Err(e) => {
            Err( PyOSError::new_err(errors_to_string(&e)) )
        },
    };
}

#[pyfunction]
/// The absolute path location of the MathCAT Rules dir.
/// IMPORTANT: This should be the first call to MathCAT
pub fn SetRulesDir(_py: Python, rules_dir_location: String) -> PyResult<()> {
    return convert_error( set_rules_dir(rules_dir_location) );
}

#[pyfunction]
/// The MathML to be spoken, brailled, or navigated.
///
/// This will override any previous MathML that was set.
/// Returns: the MathML that was set, annotated with 'id' values on each node (if none were present)
/// The 'id' values can be used during navigation for highlighting the current node
pub fn SetMathML(_py: Python, mathml_str: String) -> PyResult<String> {
    return convert_error( set_mathml(mathml_str) );
}

#[pyfunction]
/// Get the version number (e.g., "0.2.0") of MathCAT.
pub fn GetVersion(_py: Python) -> PyResult<String> {
    return Ok( get_version() );
}

#[pyfunction]
/// Returns a list of all supported languages (["en", "es", ...])
pub fn GetSupportedLanguages(_py: Python) -> PyResult<Vec<String>> {  // type in Python is list[str]
    return convert_error(get_supported_languages());
}

#[pyfunction]
/// Returns a list of all supported speech styles given a language (["ClearSpeak", "SimpleSpeak", ...])
pub fn GetSupportedSpeechStyles(_py: Python, lang: String) -> PyResult<Vec<String>> {  // type in Python is list[str]
    return convert_error(get_supported_speech_styles(lang));
}

#[pyfunction]
/// Returns a list of all supported braille codes (["UEB", "Nemeth", ...])
pub fn GetSupportedBrailleCodes(_py: Python) -> PyResult<Vec<String>> {  // type in Python is list[str]
    return convert_error(get_supported_braille_codes());
}

#[pyfunction]
/// Get the spoken text of the MathML that was set.
/// The speech takes into account any AT or user preferences.
pub fn GetSpokenText(_py: Python) -> PyResult<String> {
    return convert_error( get_spoken_text() );
}

#[pyfunction]
/// Set an API preference. The preference name should be a known preference name.
/// The value should either be a string or a number (depending upon the preference being set)
///
/// This function can be called multiple times to set different values.
/// The values are persistent but can be overwritten by setting a preference with the same name and a different value.
pub fn SetPreference(_py: Python, name: String, value: String) -> PyResult<()> {
    return convert_error( set_preference(name, value) );
}

#[pyfunction]
/// Set an API preference. The preference name should be a known preference name.
/// The value should either be a string or a number (depending upon the preference being set)
///
/// This function can be called multiple times to set different values.
/// The values are persistent but can be overwritten by setting a preference with the same name and a different value.
pub fn GetPreference(_py: Python, name: String) -> PyResult<String> {
    return match get_preference(name.clone()) {
        Ok(value) => Ok(value),
        Err(_e) => Err( PyOSError::new_err(format!("Unknown preference name {}", &name)) ),
    }
}

#[pyfunction]
/// Get the braille associated with the MathML node with a given id (MathML set by `SetMathML`]).
/// An empty string can be used to return the braille associated with the entire expression.
///
/// The braille returned depends upon the preference for braille output.
pub fn GetBraille(_py: Python, nav_node_id: String) -> PyResult<String> {
    return convert_error( get_braille(nav_node_id) );
}

#[pyfunction]
/// Get the braille associated with the MathML node with a given id (MathML set by `SetMathML`]).
/// An empty string can be used to return the braille associated with the entire expression.
///
/// The braille returned depends upon the preference for braille output.
pub fn GetNavigationBraille(_py: Python) -> PyResult<String> {
    return convert_error( get_navigation_braille() );
}

#[pyfunction]
/// Given a key code along with the modifier keys, the current node is moved accordingly (or value reported in some cases).
///
/// The spoken text for the new current node is returned.
pub fn DoNavigateKeyPress(_py: Python, key: usize, shift_key: bool, control_key: bool, alt_key: bool, meta_key: bool) -> PyResult<String> {
    return convert_error( do_navigate_keypress(key, shift_key, control_key, alt_key, meta_key) );
}

#[pyfunction]
/// Given a command, the current node is moved accordingly (or value reported in some cases).
///
/// The spoken text for the new current node is returned.
///
/// The list of legal commands are:
/// "MovePrevious", "MoveNext", "MoveStart", "MoveEnd", "MoveLineStart", "MoveLineEnd",
/// "MoveCellPrevious", "MoveCellNext", "MoveCellUp", "MoveCellDown", "MoveColumnStart", "MoveColumnEnd",
/// "ZoomIn", "ZoomOut", "ZoomOutAll", "ZoomInAll",
/// "MoveLastLocation",
/// "ReadPrevious", "ReadNext", "ReadCurrent", "ReadCellCurrent", "ReadStart", "ReadEnd", "ReadLineStart", "ReadLineEnd",
/// "DescribePrevious", "DescribeNext", "DescribeCurrent",
/// "WhereAmI", "WhereAmIAll",
/// "ToggleZoomLockUp", "ToggleZoomLockDown", "ToggleSpeakMode",
/// "Exit",
/// "MoveTo0","MoveTo1","MoveTo2","MoveTo3","MoveTo4","MoveTo5","MoveTo6","MoveTo7","MoveTo8","MoveTo9",
/// "Read0","Read1","Read2","Read3","Read4","Read5","Read6","Read7","Read8","Read9",
/// "Describe0","Describe1","Describe2","Describe3","Describe4","Describe5","Describe6","Describe7","Describe8","Describe9",
/// "SetPlacemarker0","SetPlacemarker1","SetPlacemarker2","SetPlacemarker3","SetPlacemarker4","SetPlacemarker5","SetPlacemarker6","SetPlacemarker7","SetPlacemarker8","SetPlacemarker9",
pub fn DoNavigateCommand(_py: Python, command: String) -> PyResult<String> {
    return convert_error( do_navigate_command(command) );
}

#[pyfunction]
/// Return the MathML associated with the current (navigation) node.
pub fn GetNavigationMathMLId(_py: Python) -> PyResult<(String, usize)> {
    return convert_error( get_navigation_mathml_id() );
}

#[pyfunction]
/// Return the MathML associated with the current (navigation) node.
pub fn GetNavigationMathML(_py: Python) -> PyResult<(String, usize)> {
    return convert_error( get_navigation_mathml() );
}

#[pymodule]
fn libmathcat_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(SetRulesDir, m)?)?;
    m.add_function(wrap_pyfunction!(SetMathML, m)?)?;
    m.add_function(wrap_pyfunction!(GetVersion, m)?)?;
    m.add_function(wrap_pyfunction!(GetSupportedLanguages, m)?)?;
    m.add_function(wrap_pyfunction!(GetSupportedSpeechStyles, m)?)?;
    m.add_function(wrap_pyfunction!(GetSupportedBrailleCodes, m)?)?;
    m.add_function(wrap_pyfunction!(GetSpokenText, m)?)?;
    m.add_function(wrap_pyfunction!(SetPreference, m)?)?;
    m.add_function(wrap_pyfunction!(GetPreference, m)?)?;
    m.add_function(wrap_pyfunction!(GetBraille, m)?)?;
    m.add_function(wrap_pyfunction!(GetNavigationBraille, m)?)?;
    m.add_function(wrap_pyfunction!(DoNavigateKeyPress, m)?)?;
    m.add_function(wrap_pyfunction!(DoNavigateCommand, m)?)?;
    m.add_function(wrap_pyfunction!(GetNavigationMathMLId, m)?)?;
    m.add_function(wrap_pyfunction!(GetNavigationMathML, m)?)?;

    return Ok( () );
}

#[cfg(test)]
mod py_tests {
    use super::*;

    #[test]
    fn test_setting() {
        // this isn't a real test
        Python::initialize();
        let mathml_str = "<math><mo>(</mo><mrow><mn>451</mn><mo>,</mo><mn>231</mn></mrow><mo>)</mo></math>";
        match convert_error( libmathcat::interface::set_mathml(mathml_str.to_string()) ) {
            Ok(_mathml_with_ids) => println!("MathML is set w/o error"),
            Err(e) => println!("Error is {}", e.to_string()),
        }
        // still alive?
        match convert_error( libmathcat::interface::set_mathml(mathml_str.to_string()) ) {
            Ok(_mathml_with_ids) => panic!("MathML is set 2nd time w/o error"),
            Err(e) => panic!("Error remains {}", e.to_string()),
        }
    }
}
