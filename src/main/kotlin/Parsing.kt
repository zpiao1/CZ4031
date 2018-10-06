import org.xml.sax.Attributes
import org.xml.sax.helpers.DefaultHandler
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.io.PrintWriter
import javax.xml.parsers.SAXParserFactory

val FIELDS = listOf("type", "pubkey") + "title|year|crossref".split("|")

val ELEMENTS = "article|inproceedings|proceedings|book|incollection".split("|").toHashSet()

fun main(args: Array<String>) {
    System.setProperty("jdk.xml.entityExpansionLimit", "0")
    val factory = SAXParserFactory.newInstance()
    val saxParser = factory.newSAXParser()
    println("Enter the filename:")
    val filename = readLine()
    println("Enter output path:")
    val path = readLine()
    if (filename != null && path != null) {
        Handler(path).use {
            saxParser.parse(filename, it)
        }
    }
}

class Handler(outputPath: String) : DefaultHandler(), AutoCloseable {
    private val elements = mutableListOf<String>()
    private val map = hashMapOf<String, Any>()
    private var authorIndex = -1

    private val publicationFile = PrintWriter(
        OutputStreamWriter(
            FileOutputStream("$outputPath${File.separatorChar}publication.csv"),
            Charsets.UTF_8
        ), true
    )
    private val authorFile = PrintWriter(
        OutputStreamWriter(
            FileOutputStream("$outputPath${File.separatorChar}author.csv"),
            Charsets.UTF_8
        ), true
    )
    private val publication_authorFile = PrintWriter(
        OutputStreamWriter(
            FileOutputStream("$outputPath${File.separatorChar}publication_author.csv"),
            Charsets.UTF_8
        ), true
    )

    init {
        publicationFile.println(FIELDS.joinToString(","))
        authorFile.println("name")
        publication_authorFile.println("publication,author")
    }

    override fun startElement(uri: String, localName: String, qName: String, attributes: Attributes) {
        elements += qName
        if (qName == "author") {
            authorIndex++
        }
        if (elements.size == 2) {
            map.clear()
            map["type"] = qName
            val pubkey = attributes.getValue("key")
            if (pubkey != null) {
                map["pubkey"] = pubkey
            }
        }
    }

    @Suppress("UNCHECKED_CAST")
    override fun characters(ch: CharArray, start: Int, length: Int) {
        val string = String(ch, start, length)
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
        elements.removeAt(elements.lastIndex)
        if (elements.size == 1) {
            map.replaceAll { _, value ->
                when (value) {
                    is String -> value.trim()
                    is List<*> -> value.map {
                        if (it is String) {
                            it.trim()
                        } else {
                            it
                        }
                    }
                    else -> value
                }
            }

            val pubkey = map["pubkey"] as String?
            val type = map["type"]
            val title = map["title"]
            val year = map["year"]
            if (qName in ELEMENTS && pubkey != null && type != null && title != null && year != null) {
                println("Writing to publication.csv...")
                publicationFile.println(FIELDS.asSequence().map { map[it] as String? ?: "NULL" }.joinToString(",") {
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
                for (author in authors) {
                    authorFile.println(author)
                }
                println("Writing to publication_author.csv...")
                for (author in authors) {
                    publication_authorFile.println("$pubkey,$author")
                }
            }

            authorIndex = -1
        }
    }

    override fun close() {
        publicationFile.close()
        authorFile.close()
        publication_authorFile.close()
    }
}