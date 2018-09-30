import org.xml.sax.Attributes
import org.xml.sax.helpers.DefaultHandler
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.io.PrintWriter
import javax.xml.parsers.SAXParserFactory

val FIELDS = listOf("type", "pubkey", "mdate") +
        "editor|title|booktitle|pages|year|address|journal|volume|number|month|url|ee|cdrom|cite|publisher|note|crossref|isbn|series|school|chapter"
                .split("|")

val ELEMENTS = "article|inproceedings|proceedings|book|incollection".split("|").toHashSet()

val PATH = "C:\\Users\\zpiao\\Desktop\\CZ4031"

fun main(args: Array<String>) {
    System.setProperty("jdk.xml.entityExpansionLimit", "0")
    val factory = SAXParserFactory.newInstance()
    val saxParser = factory.newSAXParser()
    val handler = Handler()
    println("Enter the filename:")
    val filename = readLine()
    if (filename != null) {
        saxParser.parse(filename, handler)
        handler.dispose()
    }
}

class Handler : DefaultHandler() {
    private val elements = mutableListOf<String>()
    private val map = hashMapOf<String, Any>()
    private var authorIndex = -1

    private val publicationFile = PrintWriter(OutputStreamWriter(FileOutputStream("$PATH\\publication.csv"), Charsets.UTF_8), true)
    private val authorFile = PrintWriter(OutputStreamWriter(FileOutputStream("$PATH\\author.csv"), Charsets.UTF_8), true)
    private val publication_authorFile = PrintWriter(OutputStreamWriter(FileOutputStream("$PATH\\publication_author.csv"), Charsets.UTF_8), true)

    init {
        publicationFile.println(FIELDS.joinToString(","))
        authorFile.println("name")
        publication_authorFile.println("publication,author")
    }

    override fun startElement(uri: String, localName: String, qName: String, attributes: Attributes) {
//        println("startElement: qName=$qName")
//        val summary = attributes.summary
//        if (summary.isNotBlank()) {
//            print(summary)
//        }
        elements += qName
        if (qName == "author") {
            authorIndex++
        }
        if (elements.size == 2) {
            map["type"] = qName
            val pubkey = attributes.getValue("key")
            if (pubkey != null) {
                map["pubkey"] = pubkey
            }
            val mdate = attributes.getValue("mdate")
            if (mdate != null) {
                map["mdate"] = mdate
            }
        }
    }

    @Suppress("UNCHECKED_CAST")
    override fun characters(ch: CharArray, start: Int, length: Int) {
        val string = String(ch, start, length)
//        println("characters: $string")
        if (elements.last() == "author") {
            val authorList = map.getOrPut("author") { mutableListOf<String>() } as MutableList<String>
            if (authorList.size <= authorIndex) {
                authorList += string
            } else {
                authorList[authorIndex] += string
            }
        } else if (elements.size > 3) {
            val element = elements[2]
            if (element == "title") {
                val existingTitle = map[element] as String?
                if (existingTitle == null) {
                    map[element] = string
                } else {
                    map[element] = existingTitle + string
                }
            } else {
                println("characters: $elements")
            }
        } else {
            val currentElement = elements.last()
            val existingValue = map[currentElement] as String?
            if (existingValue == null) {
                map[currentElement] = string
            } else {
                map[currentElement] = existingValue + string
            }
        }
    }

    @Suppress("UNCHECKED_CAST")
    override fun endElement(uri: String, localName: String, qName: String) {
//        println("endElement: qName=$qName")
        elements.removeAt(elements.lastIndex)
        if (elements.size == 1) {
            map.replaceAll { _, u ->
                when (u) {
                    is String -> u.trim()
                    is List<*> -> u.map {
                        if (it is String) {
                            it.trim()
                        } else {
                            it
                        }
                    }
                    else -> u
                }
            }
//            println(map)

            if (qName in ELEMENTS) {
                println("Writing to publication.csv...")
                publicationFile.println(FIELDS.asSequence().map { map[it] as String? ?: "" }.joinToString(",") {
                    val doubleQuoted = if ('"' in it) {
                        it.replace("\"", "\"\"")
                    } else {
                        it
                    }
                    if ('"' in doubleQuoted || ',' in doubleQuoted) {
                        "\"$doubleQuoted\""
                    } else {
                        doubleQuoted
                    }
                })
                println("Writing to author.csv...")
                val authors = map["author"] as List<String>? ?: listOf()
                authorFile.println(authors.joinToString("\n"))
                println("Writing to publication_author.csv...")
                val pubkey = map["pubkey"] as String? ?: ""
                for (author in authors) {
                    publication_authorFile.println("$pubkey,$author")
                }
            }

            map.clear()
            authorIndex = -1
        }
    }

    fun dispose() {
        publicationFile.close()
        authorFile.close()
        publication_authorFile.close()
    }
}

val Attributes.summary: String
    get() {
        val stringBuilder = StringBuilder()
        repeat(length) {
            val type = getType(it)
            val qName = getQName(it)
            val value = getValue(it)
            stringBuilder.append("type=$type, qName=$qName, value=$value\n")
        }
        return stringBuilder.toString()
    }